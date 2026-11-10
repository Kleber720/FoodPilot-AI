import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../App';
import type {
  UploadItem,
  UploadListResponse,
  UploadMetricsResponse,
  ValidationErrorResponse,
} from '../types/api';

const sampleUploadItem: UploadItem = {
  upload_id: 'upload-sample-001',
  filename: 'sample_orders.csv',
  created_at: '2026-11-09T18:30:00Z',
  total_rows: 82,
  valid_orders_count: 50,
  canceled_orders_count: 5,
  summary_metrics: {
    gross_revenue: 5000.0,
    discount_total: 250.0,
    net_revenue: 4750.0,
    average_ticket_gross: 100.0,
    average_ticket_net: 95.0,
    canceled_revenue_loss: 514.0,
    top_abc_item: 'Combo Burger Duplo Artesanal',
  },
};

const sampleMetricsResponse: UploadMetricsResponse = {
  upload_id: 'upload-sample-001',
  filename: 'sample_orders.csv',
  created_at: '2026-11-09T18:30:00Z',
  total_rows: 82,
  financials: {
    gross_revenue: 5000.0,
    discount_total: 250.0,
    net_revenue: 4750.0,
    valid_orders_count: 50,
    canceled_orders_count: 5,
    canceled_revenue_loss: 514.0,
    average_ticket_gross: 100.0,
    average_ticket_net: 95.0,
  },
  abc_curve: [
    {
      item_name: 'Combo Burger Duplo Artesanal',
      category: 'Combos',
      quantity_sold: 25,
      revenue: 2000.0,
      revenue_share_pct: 40.0,
      cumulative_share_pct: 40.0,
      abc_class: 'A',
    },
    {
      item_name: 'Porcao Batata Rustica Trufada',
      category: 'Porcoes',
      quantity_sold: 14,
      revenue: 490.0,
      revenue_share_pct: 9.8,
      cumulative_share_pct: 89.0,
      abc_class: 'B',
    },
    {
      item_name: 'Refrigerante Lata 350ml',
      category: 'Bebidas',
      quantity_sold: 5,
      revenue: 45.0,
      revenue_share_pct: 0.9,
      cumulative_share_pct: 100.0,
      abc_class: 'C',
    },
  ],
  bottlenecks: {
    prep_time_threshold_minutes: 30,
    delayed_orders_count: 5,
    delayed_items_count: 6,
    average_prep_time_minutes: 18.55,
    max_prep_time_minutes: 46.0,
    delayed_by_category: [
      {
        category: 'Burgers',
        delayed_items_count: 4,
        avg_prep_time_minutes: 39.0,
      },
      {
        category: 'Combos',
        delayed_items_count: 2,
        avg_prep_time_minutes: 40.0,
      },
    ],
    canceled_by_channel: [
      {
        channel: 'delivery',
        canceled_orders_count: 4,
        total_orders_count: 20,
        cancellation_rate_pct: 20.0,
        canceled_revenue_loss: 474.0,
      },
      {
        channel: 'app',
        canceled_orders_count: 1,
        total_orders_count: 20,
        cancellation_rate_pct: 5.0,
        canceled_revenue_loss: 40.0,
      },
      {
        channel: 'balcao',
        canceled_orders_count: 0,
        total_orders_count: 15,
        cancellation_rate_pct: 0.0,
        canceled_revenue_loss: 0.0,
      },
    ],
    canceled_by_item: [
      {
        item_name: 'Combo Burger Duplo Artesanal',
        category: 'Combos',
        canceled_quantity: 3,
        canceled_revenue_loss: 240.0,
      },
    ],
    anomalies: [
      {
        type: 'high_prep_time',
        severity: 'warning',
        dimension: 'Burgers',
        description: "4 itens na categoria 'Burgers' ultrapassaram o limite de 30 minutos de preparo.",
        metric_value: 39.0,
        threshold_value: 30.0,
      },
      {
        type: 'high_cancellation_rate',
        severity: 'critical',
        dimension: 'delivery',
        description:
          "Taxa de cancelamento no canal 'delivery' atingiu 20.0%, acima do limite tolerado de 10.0%.",
        metric_value: 20.0,
        threshold_value: 10.0,
      },
    ],
  },
  by_channel: [
    {
      channel: 'delivery',
      valid_orders_count: 16,
      quantity_sold: 43,
      gross_revenue: 2128.0,
      discount_total: 90.0,
      net_revenue: 2038.0,
      revenue_share_pct: 42.91,
      average_ticket_net: 127.38,
    },
    {
      channel: 'app',
      valid_orders_count: 19,
      quantity_sold: 41,
      gross_revenue: 1823.0,
      discount_total: 90.0,
      net_revenue: 1733.0,
      revenue_share_pct: 36.48,
      average_ticket_net: 91.21,
    },
    {
      channel: 'balcao',
      valid_orders_count: 15,
      quantity_sold: 24,
      gross_revenue: 1049.0,
      discount_total: 70.0,
      net_revenue: 979.0,
      revenue_share_pct: 20.61,
      average_ticket_net: 65.27,
    },
  ],
  by_category: [
    {
      category: 'Combos',
      quantity_sold: 25,
      gross_revenue: 2000.0,
      discount_total: 120.0,
      net_revenue: 1880.0,
      revenue_share_pct: 39.58,
      average_prep_time_minutes: 26.88,
    },
    {
      category: 'Burgers',
      quantity_sold: 43,
      gross_revenue: 1960.0,
      discount_total: 85.0,
      net_revenue: 1875.0,
      revenue_share_pct: 39.47,
      average_prep_time_minutes: 22.5,
    },
    {
      category: 'Bebidas',
      quantity_sold: 5,
      gross_revenue: 45.0,
      discount_total: 0.0,
      net_revenue: 45.0,
      revenue_share_pct: 0.95,
      average_prep_time_minutes: 2.0,
    },
  ],
};

function createJsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

describe('FoodPilot AI — Dashboard e Upload Web (Entrega 0002)', () => {
  const fetchMock = vi.fn();
  const queue: Response[] = [];

  beforeEach(() => {
    fetchMock.mockReset();
    queue.length = 0;

    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/v1/ai/status')) {
        return Promise.resolve(
          createJsonResponse(200, {
            ollama_reachable: false,
            base_url: 'http://localhost:11434',
            model: 'qwen3:4b-instruct',
            model_available: false,
          })
        );
      }
      if (url.includes('/recommendations')) {
        return Promise.resolve(
          createJsonResponse(200, {
            upload_id: 'upload-sample-001',
            generated_at: '2026-11-10T00:00:00Z',
            source: 'deterministic_fallback',
            model: 'fallback-v1',
            prompt_version: 'rec-v1',
            warnings: [],
            recommendations: [],
          })
        );
      }
      if (url.includes('/report')) {
        return Promise.resolve(
          createJsonResponse(200, {
            upload_id: 'upload-sample-001',
            filename: 'sample_orders.csv',
            generated_at: '2026-11-10T00:00:00Z',
            financials: sampleMetricsResponse.financials,
            top_abc_items: [sampleMetricsResponse.abc_curve[0]],
            anomalies: sampleMetricsResponse.bottlenecks.anomalies,
            recommendations: [],
            recommendations_source: 'deterministic_fallback',
            report_markdown: '# Relatório Executivo Demo',
          })
        );
      }
      if (queue.length > 0) {
        return Promise.resolve(queue.shift()!);
      }
      return Promise.resolve(createJsonResponse(200, { items: [], total: 0 }));
    });

    vi.stubGlobal('fetch', fetchMock);
  });

  const enqueue = (...responses: Response[]) => {
    queue.push(...responses);
  };

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('1. Exibe estado vazio orientativo quando GET /api/v1/uploads retorna items=[] e total=0', async () => {
    const emptyList: UploadListResponse = { items: [], total: 0 };
    enqueue(createJsonResponse(200, emptyList));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Nenhum lote CSV importado ainda/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Bem-vindo ao FoodPilot AI/i)).toBeInTheDocument();
    expect(screen.queryByTestId('kpi-gross-revenue')).not.toBeInTheDocument();
  });

  it('2. Realiza upload CSV com sucesso (201 Created) e carrega automaticamente KPIs, Curva ABC e Anomalias', async () => {
    const emptyList: UploadListResponse = { items: [], total: 0 };
    enqueue(
      createJsonResponse(200, emptyList),
      createJsonResponse(201, sampleUploadItem),
      createJsonResponse(200, sampleMetricsResponse)
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Bem-vindo ao FoodPilot AI/i)).toBeInTheDocument();
    });

    const fileInput = screen.getByLabelText(/Arquivo CSV de pedidos/i);
    const csvFile = new File(
      ['order_id,timestamp,item_name,category,quantity,unit_price,discount,prep_time_minutes,status,channel\n'],
      'sample_orders.csv',
      { type: 'text/csv' }
    );

    fireEvent.change(fileInput, { target: { files: [csvFile] } });

    const submitButton = screen.getByRole('button', { name: /Enviar e Processar CSV/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId('kpi-gross-revenue')).toHaveTextContent('R$ 5.000,00');
    });

    expect(screen.getByTestId('kpi-net-revenue')).toHaveTextContent('R$ 4.750,00');
    expect(screen.getByTestId('kpi-discount-total')).toHaveTextContent('R$ 250,00');
    expect(screen.getByTestId('kpi-avg-ticket-gross')).toHaveTextContent('R$ 100,00');
    expect(screen.getByTestId('kpi-avg-ticket-net')).toHaveTextContent('R$ 95,00');
    expect(screen.getByTestId('kpi-valid-orders')).toHaveTextContent('50');
    expect(screen.getByTestId('kpi-canceled-orders')).toHaveTextContent('5');
    expect(screen.getByTestId('kpi-canceled-loss')).toHaveTextContent('R$ 514,00');

    // Verifica Curva ABC e Anomalias carregadas
    const abcTable = screen.getByRole('table', { name: /Tabela da Curva ABC de produtos/i });
    expect(within(abcTable).getByText('Combo Burger Duplo Artesanal')).toBeInTheDocument();
    expect(within(abcTable).getByText('Porcao Batata Rustica Trufada')).toBeInTheDocument();
    expect(within(abcTable).getByText('Refrigerante Lata 350ml')).toBeInTheDocument();

    expect(
      screen.getByText(/4 itens na categoria 'Burgers' ultrapassaram o limite de 30 minutos/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Taxa de cancelamento no canal 'delivery' atingiu 20.0%/i)
    ).toBeInTheDocument();
  });

  it('3. Exibe alerta e tabela de erros linha/coluna quando POST /api/v1/uploads retorna 422 Unprocessable Entity', async () => {
    const emptyList: UploadListResponse = { items: [], total: 0 };
    const errorPayload422: ValidationErrorResponse = {
      detail: 'Arquivo CSV inválido: foram encontrados erros de validação.',
      errors: [
        {
          row: 4,
          column: 'unit_price',
          message: 'Valor numérico deve ser estritamente maior que zero (recebido: -15.0).',
        },
        {
          row: null,
          column: 'prep_time_minutes',
          message: "Coluna obrigatória 'prep_time_minutes' ausente no cabeçalho do CSV.",
        },
      ],
    };

    enqueue(createJsonResponse(200, emptyList), createJsonResponse(422, errorPayload422));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Bem-vindo ao FoodPilot AI/i)).toBeInTheDocument();
    });

    const fileInput = screen.getByLabelText(/Arquivo CSV de pedidos/i);
    const badFile = new File(['invalid,csv'], 'invalido.csv', { type: 'text/csv' });
    fireEvent.change(fileInput, { target: { files: [badFile] } });

    const submitButton = screen.getByRole('button', { name: /Enviar e Processar CSV/i });
    await userEvent.click(submitButton);

    const alertRegion = await screen.findByRole('alert');
    expect(alertRegion).toHaveTextContent(
      'Arquivo CSV inválido: foram encontrados erros de validação.'
    );

    const errorTable = screen.getByRole('table', {
      name: /Erros de validação do arquivo CSV/i,
    });
    expect(within(errorTable).getByText('4')).toBeInTheDocument();
    expect(within(errorTable).getByText('unit_price')).toBeInTheDocument();
    expect(
      within(errorTable).getByText(
        'Valor numérico deve ser estritamente maior que zero (recebido: -15.0).'
      )
    ).toBeInTheDocument();
    expect(within(errorTable).getByText('Cabeçalho / Arquivo')).toBeInTheDocument();
    expect(within(errorTable).getByText('prep_time_minutes')).toBeInTheDocument();
  });

  it('4. Permite filtrar interativamente a Curva ABC por classe (A, B, C), Canal e Categoria', async () => {
    const populatedList: UploadListResponse = {
      items: [sampleUploadItem],
      total: 1,
    };

    enqueue(createJsonResponse(200, populatedList), createJsonResponse(200, sampleMetricsResponse));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('kpi-gross-revenue')).toHaveTextContent('R$ 5.000,00');
    });

    const abcTable = screen.getByRole('table', { name: /Tabela da Curva ABC de produtos/i });

    // Filtra apenas Classe A
    const classAButton = screen.getByRole('button', { name: 'Classe A' });
    await userEvent.click(classAButton);
    expect(classAButton).toHaveAttribute('aria-pressed', 'true');
    expect(within(abcTable).getByText('Combo Burger Duplo Artesanal')).toBeInTheDocument();
    expect(within(abcTable).queryByText('Porcao Batata Rustica Trufada')).not.toBeInTheDocument();
    expect(within(abcTable).queryByText('Refrigerante Lata 350ml')).not.toBeInTheDocument();

    // Filtra apenas Classe B
    const classBButton = screen.getByRole('button', { name: 'Classe B' });
    await userEvent.click(classBButton);
    expect(within(abcTable).getByText('Porcao Batata Rustica Trufada')).toBeInTheDocument();
    expect(within(abcTable).queryByText('Combo Burger Duplo Artesanal')).not.toBeInTheDocument();

    // Filtra apenas Classe C
    const classCButton = screen.getByRole('button', { name: 'Classe C' });
    await userEvent.click(classCButton);
    expect(within(abcTable).getByText('Refrigerante Lata 350ml')).toBeInTheDocument();
    expect(within(abcTable).queryByText('Porcao Batata Rustica Trufada')).not.toBeInTheDocument();

    // Filtra por Canal (delivery)
    const channelTable = screen.getByRole('table', { name: /Tabela de desempenho por canal/i });
    const deliveryFilterBtn = screen.getByRole('button', { name: /Delivery \(delivery\)/i });
    await userEvent.click(deliveryFilterBtn);
    expect(within(channelTable).getByText('R$ 2.038,00')).toBeInTheDocument();
    expect(within(channelTable).queryByText('R$ 1.733,00')).not.toBeInTheDocument();

    // Filtra por Categoria (Bebidas)
    const categoryTable = screen.getByRole('table', {
      name: /Tabela de desempenho por categoria/i,
    });
    const bebidasFilterBtn = screen.getByRole('button', { name: 'Bebidas' });
    await userEvent.click(bebidasFilterBtn);
    expect(within(categoryTable).getByText('Bebidas')).toBeInTheDocument();
    expect(within(categoryTable).queryByText('Combos')).not.toBeInTheDocument();
  });

  it('5. Permite alternar entre lotes no histórico disparando GET /api/v1/uploads/{id}/metrics', async () => {
    const secondUploadItem: UploadItem = {
      ...sampleUploadItem,
      upload_id: 'upload-sample-002',
      filename: 'second_week.csv',
      summary_metrics: {
        ...sampleUploadItem.summary_metrics,
        gross_revenue: 3200.0,
        net_revenue: 3000.0,
      },
    };

    const secondMetricsResponse: UploadMetricsResponse = {
      ...sampleMetricsResponse,
      upload_id: 'upload-sample-002',
      filename: 'second_week.csv',
      financials: {
        ...sampleMetricsResponse.financials,
        gross_revenue: 3200.0,
        net_revenue: 3000.0,
      },
    };

    const multiList: UploadListResponse = {
      items: [sampleUploadItem, secondUploadItem],
      total: 2,
    };

    enqueue(
      createJsonResponse(200, multiList),
      createJsonResponse(200, sampleMetricsResponse),
      createJsonResponse(200, secondMetricsResponse)
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTestId('kpi-gross-revenue')).toHaveTextContent('R$ 5.000,00');
    });

    const historySelect = screen.getByLabelText(/Lote ativo em exibição/i);
    await userEvent.selectOptions(historySelect, 'upload-sample-002');

    await waitFor(() => {
      expect(screen.getByTestId('kpi-gross-revenue')).toHaveTextContent('R$ 3.200,00');
    });
    expect(screen.getByTestId('kpi-net-revenue')).toHaveTextContent('R$ 3.000,00');
  });
});
