import React from 'react';
import type { BottlenecksReport } from '../types/api';
import {
  formatChannelLabel,
  formatCurrencyBRL,
  formatMinutes,
  formatPercent,
} from '../utils/formatters';

export interface BottlenecksAndAnomaliesSectionProps {
  bottlenecks: BottlenecksReport;
}

export const BottlenecksAndAnomaliesSection: React.FC<BottlenecksAndAnomaliesSectionProps> = ({
  bottlenecks,
}) => {
  return (
    <section className="panel-card" aria-labelledby="bottlenecks-heading">
      <div className="section-header">
        <div>
          <h2 id="bottlenecks-heading" className="section-title">
            Diagnóstico de Gargalos Operacionais e Anomalias (RN-06)
          </h2>
          <p className="section-subtitle">
            Monitoramento determinístico de atrasos na cozinha (limite &gt;{' '}
            {bottlenecks.prep_time_threshold_minutes} min) e taxas de cancelamento por canal e produto.
          </p>
        </div>
        <span
          className={`badge ${
            bottlenecks.anomalies.some((a) => a.severity === 'critical')
              ? 'badge-critical'
              : bottlenecks.anomalies.length > 0
                ? 'badge-warning'
                : 'badge-success'
          }`}
        >
          {bottlenecks.anomalies.length} anomalia(s) detectada(s)
        </span>
      </div>

      {/* Painel de Alertas Determinísticos (anomalies) */}
      <h3 style={{ fontSize: '1rem', marginTop: 0, marginBottom: '0.75rem' }}>
        Alertas Operacionais Acionados
      </h3>
      {bottlenecks.anomalies.length === 0 ? (
        <div className="alert-box alert-box--success" role="status" style={{ marginBottom: '1.5rem' }}>
          Nenhuma anomalia operacional detectada neste lote. Todos os canais e categorias operaram dentro dos limites.
        </div>
      ) : (
        <div className="anomaly-list" role="list" aria-label="Alertas de anomalias operacionais">
          {bottlenecks.anomalies.map((anomaly, index) => (
            <article
              key={`${anomaly.type}-${anomaly.dimension}-${index}`}
              role="listitem"
              className={`anomaly-card anomaly-card--${anomaly.severity}`}
            >
              <div className="anomaly-header">
                <span className="anomaly-dimension">{anomaly.dimension}</span>
                <span
                  className={`badge ${
                    anomaly.severity === 'critical' ? 'badge-critical' : 'badge-warning'
                  }`}
                >
                  {anomaly.severity === 'critical' ? 'Crítico (critical)' : 'Atenção (warning)'}
                </span>
              </div>
              <p className="anomaly-description">{anomaly.description}</p>
              <div className="anomaly-footer">
                Tipo: <code>{anomaly.type}</code> | Medido: <strong>{anomaly.metric_value}</strong>{' '}
                (Limite: {anomaly.threshold_value})
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Indicadores de Tempo de Preparo */}
      <div className="kpi-grid" style={{ marginBottom: '1.5rem' }}>
        <article className="kpi-card">
          <span className="kpi-label">Limiar de Atraso</span>
          <span className="kpi-value">{bottlenecks.prep_time_threshold_minutes} min</span>
          <span className="kpi-meta">Parâmetro fixo RN-06</span>
        </article>

        <article className="kpi-card">
          <span className="kpi-label">Pedidos Atrasados</span>
          <span className="kpi-value" data-testid="bottleneck-delayed-orders">
            {bottlenecks.delayed_orders_count}
          </span>
          <span className="kpi-meta">Pedidos concluídos com preparo &gt; 30 min</span>
        </article>

        <article className="kpi-card">
          <span className="kpi-label">Itens Atrasados</span>
          <span className="kpi-value" data-testid="bottleneck-delayed-items">
            {bottlenecks.delayed_items_count}
          </span>
          <span className="kpi-meta">Linhas de itens com preparo &gt; 30 min</span>
        </article>

        <article className="kpi-card">
          <span className="kpi-label">Tempo Médio de Preparo</span>
          <span className="kpi-value">
            {formatMinutes(bottlenecks.average_prep_time_minutes)}
          </span>
          <span className="kpi-meta">
            Pico máximo: {formatMinutes(bottlenecks.max_prep_time_minutes)}
          </span>
        </article>
      </div>

      {/* Tabelas de Atrasos por Categoria e Cancelamentos */}
      <div className="split-grid">
        <div>
          <h3 style={{ fontSize: '1rem', marginTop: 0 }}>
            Atrasos de Preparo por Categoria (&gt; {bottlenecks.prep_time_threshold_minutes} min)
          </h3>
          {bottlenecks.delayed_by_category.length === 0 ? (
            <p className="field-hint">Nenhum item ultrapassou o limite de preparo neste lote.</p>
          ) : (
            <div className="table-container">
              <table className="data-table" aria-label="Atrasos de preparo por categoria">
                <thead>
                  <tr>
                    <th scope="col">Categoria</th>
                    <th scope="col" className="num-col">
                      Itens Atrasados
                    </th>
                    <th scope="col" className="num-col">
                      Média dos Atrasados
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {bottlenecks.delayed_by_category.map((row) => (
                    <tr key={row.category}>
                      <td>
                        <strong>{row.category}</strong>
                      </td>
                      <td className="num-col">{row.delayed_items_count}</td>
                      <td className="num-col">{formatMinutes(row.avg_prep_time_minutes)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div>
          <h3 style={{ fontSize: '1rem', marginTop: 0 }}>Taxa de Cancelamento por Canal</h3>
          {bottlenecks.canceled_by_channel.length === 0 ? (
            <p className="field-hint">Sem dados de canal neste lote.</p>
          ) : (
            <div className="table-container">
              <table className="data-table" aria-label="Cancelamentos por canal">
                <thead>
                  <tr>
                    <th scope="col">Canal</th>
                    <th scope="col" className="num-col">
                      Cancelados / Total
                    </th>
                    <th scope="col" className="num-col">
                      Taxa (%)
                    </th>
                    <th scope="col" className="num-col">
                      Perda Bruta
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {bottlenecks.canceled_by_channel.map((row) => (
                    <tr key={row.channel}>
                      <td>
                        <strong>{formatChannelLabel(row.channel)}</strong> <code>{row.channel}</code>
                      </td>
                      <td className="num-col">
                        {row.canceled_orders_count} / {row.total_orders_count}
                      </td>
                      <td className="num-col">{formatPercent(row.cancellation_rate_pct)}</td>
                      <td className="num-col">{formatCurrencyBRL(row.canceled_revenue_loss)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Tabela de Cancelamentos por Item */}
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginTop: 0 }}>Produtos com Ocorrências de Cancelamento</h3>
        {bottlenecks.canceled_by_item.length === 0 ? (
          <p className="field-hint">Nenhum produto teve pedido cancelado neste lote.</p>
        ) : (
          <div className="table-container">
            <table className="data-table" aria-label="Cancelamentos por item do cardápio">
              <thead>
                <tr>
                  <th scope="col">Produto</th>
                  <th scope="col">Categoria</th>
                  <th scope="col" className="num-col">
                    Unidades Canceladas
                  </th>
                  <th scope="col" className="num-col">
                    Receita Perdida
                  </th>
                </tr>
              </thead>
              <tbody>
                {bottlenecks.canceled_by_item.map((item) => (
                  <tr key={item.item_name}>
                    <td>
                      <strong>{item.item_name}</strong>
                    </td>
                    <td>{item.category}</td>
                    <td className="num-col">{item.canceled_quantity}</td>
                    <td className="num-col">{formatCurrencyBRL(item.canceled_revenue_loss)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
};
