import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AiStatusBadge } from '../components/AiStatusBadge';
import { RecommendationsPanel } from '../components/RecommendationsPanel';
import type { AiStatusResponse, RecommendationsResponse } from '../types/api';

const sampleRecommendations: RecommendationsResponse = {
  upload_id: 'upload-001',
  generated_at: '2026-11-10T00:00:00Z',
  source: 'ollama',
  model: 'qwen3:4b-instruct',
  prompt_version: 'rec-v1',
  warnings: [],
  recommendations: [
    {
      rank: 1,
      title: 'Ajustar Operação do Delivery',
      theme: 'delivery',
      diagnosis: 'Taxa de cancelamento elevada em 18.75% no canal de entrega.',
      action: 'Reduzir raio de entrega nos horários de pico.',
      expected_impact: 'Redução de perdas em até R$ 648,00.',
      evidence: [
        {
          fact_id: 'channel.delivery.cancellation_rate_pct',
          label: 'Taxa de Cancelamento Delivery',
          value: 18.75,
          unit: '%',
        },
        {
          fact_id: 'channel.delivery.canceled_revenue_loss',
          label: 'Perda Estimada no Delivery',
          value: 648.0,
          unit: 'BRL',
        },
      ],
    },
    {
      rank: 2,
      title: 'Mitigar Gargalos na Cozinha',
      theme: 'prep_time',
      diagnosis: '18 pedidos ultrapassaram o tempo limite de 45 minutos.',
      action: 'Reorganizar praças de montagem.',
      expected_impact: 'Diminuir tempo médio de 34.50 min.',
      evidence: [
        {
          fact_id: 'bot.delayed_orders_count',
          label: 'Pedidos Atrasados',
          value: 18,
          unit: 'count',
        },
      ],
    },
    {
      rank: 3,
      title: 'Rever Cardápio Classe C',
      theme: 'mix_products',
      diagnosis: 'Itens de baixa rotação geram custos desnecessários.',
      action: 'Descontinuar ou reformular itens da cauda longa.',
      expected_impact: 'Foco nos produtos que geram 80% do faturamento.',
      evidence: [
        {
          fact_id: 'fin.gross_revenue',
          label: 'Faturamento Bruto',
          value: 4789.5,
          unit: 'BRL',
        },
      ],
    },
  ],
};

describe('Componentes de IA e Recomendações (Entrega 0003)', () => {
  describe('AiStatusBadge', () => {
    it('1. Exibe Online quando Ollama está acessível e modelo disponível', () => {
      const status: AiStatusResponse = {
        ollama_reachable: true,
        base_url: 'http://localhost:11434',
        model: 'qwen3:4b-instruct',
        model_available: true,
      };

      render(<AiStatusBadge aiStatus={status} />);
      const badge = screen.getByTestId('ai-status-badge');
      expect(badge).toHaveTextContent(/IA Local \(qwen3:4b-instruct\): Online/i);
      expect(badge).toHaveClass('badge-success');
    });

    it('2. Exibe Fallback Ativo quando Ollama está offline', () => {
      const status: AiStatusResponse = {
        ollama_reachable: false,
        base_url: 'http://localhost:11434',
        model: 'qwen3:4b-instruct',
        model_available: false,
      };

      render(<AiStatusBadge aiStatus={status} />);
      const badge = screen.getByTestId('ai-status-badge');
      expect(badge).toHaveTextContent(/Offline \(Fallback Determinístico Ativo\)/i);
      expect(badge).toHaveClass('badge-warning');
    });

    it('3. Exibe Modelo Ausente quando Ollama está ativo mas sem o modelo', () => {
      const status: AiStatusResponse = {
        ollama_reachable: true,
        base_url: 'http://localhost:11434',
        model: 'qwen3:4b-instruct',
        model_available: false,
      };

      render(<AiStatusBadge aiStatus={status} />);
      const badge = screen.getByTestId('ai-status-badge');
      expect(badge).toHaveTextContent(/Modelo ausente/i);
    });
  });

  describe('RecommendationsPanel', () => {
    it('4. Renderiza as 3 recomendações ordenadas por rank com evidências oficiais', () => {
      const onGenerateMock = vi.fn();

      render(
        <RecommendationsPanel
          uploadId="upload-001"
          filename="sample_orders.csv"
          recommendations={sampleRecommendations}
          isLoadingInitial={false}
          isGenerating={false}
          error={null}
          onGenerate={onGenerateMock}
        />
      );

      expect(screen.getByText(/Ajustar Operação do Delivery/i)).toBeInTheDocument();
      expect(screen.getByText(/Mitigar Gargalos na Cozinha/i)).toBeInTheDocument();
      expect(screen.getByText(/Rever Cardápio Classe C/i)).toBeInTheDocument();

      // Verifica badge de origem IA
      const sourceBadge = screen.getByTestId('recommendations-source-badge');
      expect(sourceBadge).toHaveTextContent(/Origem: Agente IA Local \(qwen3:4b-instruct\)/i);

      // Verifica formatação de evidência
      expect(screen.getByText('18,75%')).toBeInTheDocument();
      expect(screen.getByText('R$ 648,00')).toBeInTheDocument();
      expect(screen.getByText('18')).toBeInTheDocument();
      expect(screen.getByText('R$ 4.789,50')).toBeInTheDocument();
    });

    it('5. Dispara callback de regerar recomendações ao clicar no botão', async () => {
      const onGenerateMock = vi.fn();

      render(
        <RecommendationsPanel
          uploadId="upload-001"
          filename="sample_orders.csv"
          recommendations={sampleRecommendations}
          isLoadingInitial={false}
          isGenerating={false}
          error={null}
          onGenerate={onGenerateMock}
        />
      );

      const regenButton = screen.getByRole('button', { name: /Regerar Recomendações/i });
      await userEvent.click(regenButton);

      expect(onGenerateMock).toHaveBeenCalledTimes(1);
    });

    it('6. Exibe badge de fallback quando a origem for deterministic_fallback', () => {
      const fallbackRecs: RecommendationsResponse = {
        ...sampleRecommendations,
        source: 'deterministic_fallback',
        model: 'fallback-v1',
      };

      render(
        <RecommendationsPanel
          uploadId="upload-001"
          filename="sample_orders.csv"
          recommendations={fallbackRecs}
          isLoadingInitial={false}
          isGenerating={false}
          error={null}
          onGenerate={vi.fn()}
        />
      );

      const sourceBadge = screen.getByTestId('recommendations-source-badge');
      expect(sourceBadge).toHaveTextContent(/Regras Determinísticas \(Fallback/i);
    });
  });
});
