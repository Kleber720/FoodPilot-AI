import React from 'react';
import type { UploadItem } from '../types/api';
import { formatCurrencyBRL, formatDateTimeUTC } from '../utils/formatters';

export interface UploadHistorySelectorProps {
  uploads: UploadItem[];
  total: number;
  selectedUploadId: string | null;
  isLoadingMetrics: boolean;
  onSelectUpload: (uploadId: string) => void;
}

export const UploadHistorySelector: React.FC<UploadHistorySelectorProps> = ({
  uploads,
  total,
  selectedUploadId,
  isLoadingMetrics,
  onSelectUpload,
}) => {
  const activeUpload = uploads.find((u) => u.upload_id === selectedUploadId) ?? null;

  return (
    <section className="panel-card" aria-labelledby="upload-history-heading">
      <div className="section-header">
        <div>
          <h2 id="upload-history-heading" className="section-title">
            Histórico de Lotes Importados
          </h2>
          <p className="section-subtitle">
            Selecione um lote processado para inspecionar suas métricas determinísticas no dashboard.
          </p>
        </div>
        <span className="badge badge-info">Total: {total}</span>
      </div>

      {total === 0 || uploads.length === 0 ? (
        <div className="alert-box alert-box--info" role="status">
          <p className="alert-title">Nenhum lote CSV importado ainda</p>
          <p style={{ margin: 0, fontSize: '0.875rem' }}>
            Utilize o painel ao lado para enviar seu primeiro arquivo CSV de pedidos (por exemplo,{' '}
            <code>data/sample_orders.csv</code>) e liberar o dashboard executivo.
          </p>
        </div>
      ) : (
        <>
          <div className="form-field">
            <label htmlFor="upload-history-select" className="form-label">
              Lote ativo em exibição
            </label>
            <select
              id="upload-history-select"
              className="select-input"
              value={selectedUploadId ?? ''}
              onChange={(e) => onSelectUpload(e.target.value)}
              disabled={isLoadingMetrics}
            >
              {uploads.map((item) => (
                <option key={item.upload_id} value={item.upload_id}>
                  {item.filename} — {formatDateTimeUTC(item.created_at)} ({item.total_rows} linhas |{' '}
                  {item.valid_orders_count} concluídos)
                </option>
              ))}
            </select>
          </div>

          {activeUpload && (
            <div
              className="alert-box alert-box--info"
              style={{ marginTop: '0.5rem' }}
              aria-label="Resumo do lote selecionado"
            >
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  justifyContent: 'space-between',
                  gap: '0.5rem',
                  fontSize: '0.875rem',
                }}
              >
                <span>
                  <strong>Arquivo:</strong> {activeUpload.filename}
                </span>
                <span>
                  <strong>Linhas CSV:</strong> {activeUpload.total_rows}
                </span>
                <span>
                  <strong>Pedidos válidos:</strong> {activeUpload.valid_orders_count}
                </span>
                <span>
                  <strong>Cancelados:</strong> {activeUpload.canceled_orders_count}
                </span>
                <span>
                  <strong>Receita líquida:</strong>{' '}
                  {formatCurrencyBRL(activeUpload.summary_metrics.net_revenue)}
                </span>
                {activeUpload.summary_metrics.top_abc_item && (
                  <span>
                    <strong>Top 1 ABC:</strong> {activeUpload.summary_metrics.top_abc_item}
                  </span>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
};
