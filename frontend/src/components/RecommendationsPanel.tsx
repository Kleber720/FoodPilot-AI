import React from 'react';
import type { RecommendationsResponse } from '../types/api';
import {
  formatDateTimeUTC,
  formatEvidenceValue,
  formatThemeLabel,
} from '../utils/formatters';

export interface RecommendationsPanelProps {
  uploadId: string;
  filename: string;
  recommendations: RecommendationsResponse | null;
  isLoadingInitial: boolean;
  isGenerating: boolean;
  error: string | null;
  onGenerate: () => Promise<void> | void;
}

/**
 * Painel de Recomendações Fundamentadas em Fatos (`RN-07` a `RN-10` — §2.6 e §2.7 de `docs/contrato.md`).
 * Invariante: Exibe exclusivamente os valores de `evidence[].value` entregues pela API,
 * sem recalcular métricas nem extrair números do texto no cliente.
 */
export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({
  filename,
  recommendations,
  isLoadingInitial,
  isGenerating,
  error,
  onGenerate,
}) => {
  const sortedRecommendations = recommendations
    ? [...recommendations.recommendations].sort((a, b) => a.rank - b.rank)
    : [];

  return (
    <section
      className="panel-card"
      aria-labelledby="recommendations-heading"
      data-testid="recommendations-panel"
    >
      <div className="section-header">
        <div>
          <h2 id="recommendations-heading" className="section-title">
            Recomendações Práticas Fundamentadas (RN-07 a RN-10)
          </h2>
          <p className="section-subtitle">
            3 ações prioritárias auditadas contra alucinações numéricas a partir da ficha de fatos do lote{' '}
            <strong>{filename}</strong>.
          </p>
        </div>

        <div className="header-badges">
          {recommendations && (
            <>
              <span
                className={`badge ${
                  recommendations.source === 'ollama' || recommendations.source === 'llm'
                    ? 'badge-success'
                    : 'badge-warning'
                }`}
                data-testid="recommendations-source-badge"
              >
                {recommendations.source === 'ollama' || recommendations.source === 'llm'
                  ? `Origem: Agente IA Local (${recommendations.model ?? 'qwen3:4b-instruct'})`
                  : 'Origem: Regras Determinísticas (Fallback — IA indisponível)'}
              </span>
              <span className="badge badge-info" data-testid="recommendations-prompt-version">
                Prompt: {recommendations.prompt_version}
              </span>
              <span className="badge badge-info">
                Gerado em: {formatDateTimeUTC(recommendations.generated_at)}
              </span>
            </>
          )}

          {recommendations && !isGenerating && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onGenerate}
              disabled={isGenerating}
            >
              Regerar Recomendações
            </button>
          )}
        </div>
      </div>

      {isLoadingInitial ? (
        <div className="alert-box alert-box--info" role="status" aria-live="polite" aria-busy="true">
          Consultando recomendações salvas para este lote...
        </div>
      ) : isGenerating ? (
        <div
          className="alert-box alert-box--info"
          role="status"
          aria-live="polite"
          aria-busy="true"
          data-testid="recommendations-loading"
        >
          <p className="alert-title">Analisando ficha de fatos e auditando aterramento numérico...</p>
          <p style={{ margin: 0, fontSize: '0.875rem' }}>
            O modelo local (<code>qwen3:4b-instruct</code> via Ollama) ou o motor determinístico está
            elaborando as 3 recomendações prioritárias. Na primeira execução na GPU local, esta operação
            pode levar até ~90 segundos.
          </p>
        </div>
      ) : error ? (
        <div className="alert-box alert-box--error" role="alert">
          <p className="alert-title">Falha ao processar recomendações</p>
          <p style={{ margin: '0 0 0.75rem' }}>{error}</p>
          <button type="button" className="btn btn-primary" onClick={onGenerate}>
            Tentar novamente
          </button>
        </div>
      ) : !recommendations ? (
        <div className="recommendations-empty" data-testid="recommendations-empty">
          <p style={{ margin: '0 0 0.75rem', color: 'var(--color-text-secondary)' }}>
            Ainda não foram geradas recomendações para o lote <strong>{filename}</strong>. Clique no botão
            abaixo para analisar a ficha de fatos determinística e gerar 3 recomendações acionáveis.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onGenerate}
            disabled={isGenerating}
          >
            Gerar 3 Recomendações Fundamentadas
          </button>
        </div>
      ) : (
        <>
          {recommendations.warnings.length > 0 && (
            <div
              className="alert-box alert-box--warning"
              role="status"
              aria-live="polite"
              data-testid="recommendations-warnings"
              style={{ marginBottom: '1.25rem', marginTop: 0 }}
            >
              <p className="alert-title">Avisos de Execução e Degradação Graciosa (RN-09)</p>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                {recommendations.warnings.map((warn, idx) => (
                  <li key={idx}>{warn}</li>
                ))}
              </ul>
            </div>
          )}

          <div
            className="recommendations-grid"
            role="list"
            aria-label="Lista de 3 recomendações fundamentadas"
          >
            {sortedRecommendations.map((rec) => (
              <article
                key={rec.rank}
                role="listitem"
                className="recommendation-card"
                data-testid={`recommendation-card-${rec.rank}`}
              >
                <div className="recommendation-card__header">
                  <span className="recommendation-rank">#{rec.rank}</span>
                  <span className={`badge badge-theme badge-theme--${rec.theme}`}>
                    {formatThemeLabel(rec.theme)} ({rec.theme})
                  </span>
                </div>

                <h3 className="recommendation-title">{rec.title}</h3>

                <div className="recommendation-body">
                  <div className="recommendation-block">
                    <span className="recommendation-block__label">Diagnóstico Fundamentado</span>
                    <p className="recommendation-block__text">{rec.diagnosis}</p>
                  </div>

                  <div className="recommendation-block">
                    <span className="recommendation-block__label">Ação Recomendada</span>
                    <p className="recommendation-block__text">{rec.action}</p>
                  </div>

                  <div className="recommendation-block">
                    <span className="recommendation-block__label">Impacto Esperado</span>
                    <p className="recommendation-block__text">{rec.expected_impact}</p>
                  </div>
                </div>

                <div className="recommendation-evidence">
                  <span className="recommendation-block__label">
                    Evidências Auditadas na Ficha de Fatos ({rec.evidence.length})
                  </span>
                  <div className="evidence-chips" role="list" aria-label={`Evidências da recomendação ${rec.rank}`}>
                    {rec.evidence.map((ev) => (
                      <div
                        key={ev.fact_id}
                        role="listitem"
                        className="evidence-chip"
                        data-testid={`evidence-chip-${ev.fact_id}`}
                      >
                        <span className="evidence-chip__label">{ev.label}:</span>{' '}
                        <strong className="evidence-chip__value">
                          {formatEvidenceValue(ev.value, ev.unit)}
                        </strong>{' '}
                        <code className="evidence-chip__id">({ev.fact_id})</code>
                      </div>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
};
