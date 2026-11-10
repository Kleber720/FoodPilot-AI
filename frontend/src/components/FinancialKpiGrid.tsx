import React from 'react';
import type { FinancialMetrics } from '../types/api';
import { formatCurrencyBRL } from '../utils/formatters';

export interface FinancialKpiGridProps {
  financials: FinancialMetrics;
  totalRows: number;
  topAbcItem?: string | null;
}

/**
 * Grade de KPIs Financeiros Consolidados (`RN-03` e `RN-04`).
 * Invariante: Exibe estritamente os números calculados pelo back-end/pipeline, sem recálculo no cliente.
 */
export const FinancialKpiGrid: React.FC<FinancialKpiGridProps> = ({
  financials,
  totalRows,
  topAbcItem,
}) => {
  return (
    <section className="panel-card" aria-labelledby="financial-kpis-heading">
      <div className="section-header">
        <div>
          <h2 id="financial-kpis-heading" className="section-title">
            Indicadores Financeiros Consolidados
          </h2>
          <p className="section-subtitle">
            Métricas determinísticas auditadas (RN-03 e RN-04) — {totalRows} linhas processadas no lote.
            {topAbcItem ? ` Produto líder (Top 1 ABC): ${topAbcItem}.` : ''}
          </p>
        </div>
        <span className="badge badge-success">Sem recálculo no cliente</span>
      </div>

      <div className="kpi-grid">
        <article className="kpi-card" aria-label="Faturamento Bruto">
          <span className="kpi-label">Faturamento Bruto</span>
          <span className="kpi-value" data-testid="kpi-gross-revenue">
            {formatCurrencyBRL(financials.gross_revenue)}
          </span>
          <span className="kpi-meta">Soma de pedidos concluídos (RN-03)</span>
        </article>

        <article className="kpi-card" aria-label="Total de Descontos">
          <span className="kpi-label">Total de Descontos</span>
          <span className="kpi-value" data-testid="kpi-discount-total">
            {formatCurrencyBRL(financials.discount_total)}
          </span>
          <span className="kpi-meta">Descontos aplicados em pedidos concluídos</span>
        </article>

        <article className="kpi-card kpi-card--highlight" aria-label="Faturamento Líquido">
          <span className="kpi-label">Faturamento Líquido</span>
          <span className="kpi-value" data-testid="kpi-net-revenue">
            {formatCurrencyBRL(financials.net_revenue)}
          </span>
          <span className="kpi-meta">Bruto menos descontos (RN-03)</span>
        </article>

        <article className="kpi-card" aria-label="Ticket Médio Bruto">
          <span className="kpi-label">Ticket Médio Bruto</span>
          <span className="kpi-value" data-testid="kpi-avg-ticket-gross">
            {formatCurrencyBRL(financials.average_ticket_gross)}
          </span>
          <span className="kpi-meta">Por pedido concluído único (RN-04)</span>
        </article>

        <article className="kpi-card kpi-card--highlight" aria-label="Ticket Médio Líquido">
          <span className="kpi-label">Ticket Médio Líquido</span>
          <span className="kpi-value" data-testid="kpi-avg-ticket-net">
            {formatCurrencyBRL(financials.average_ticket_net)}
          </span>
          <span className="kpi-meta">Receita líquida / pedidos concluídos (RN-04)</span>
        </article>

        <article className="kpi-card" aria-label="Pedidos Concluídos">
          <span className="kpi-label">Pedidos Concluídos</span>
          <span className="kpi-value" data-testid="kpi-valid-orders">
            {financials.valid_orders_count}
          </span>
          <span className="kpi-meta">IDs de pedido únicos (completed)</span>
        </article>

        <article className="kpi-card" aria-label="Pedidos Cancelados">
          <span className="kpi-label">Pedidos Cancelados</span>
          <span className="kpi-value" data-testid="kpi-canceled-orders">
            {financials.canceled_orders_count}
          </span>
          <span className="kpi-meta">IDs de pedido únicos (canceled)</span>
        </article>

        <article className="kpi-card kpi-card--loss" aria-label="Perda por Cancelamento">
          <span className="kpi-label">Perda por Cancelamento</span>
          <span className="kpi-value" data-testid="kpi-canceled-loss">
            {formatCurrencyBRL(financials.canceled_revenue_loss)}
          </span>
          <span className="kpi-meta">Segregada do faturamento (RN-03)</span>
        </article>
      </div>
    </section>
  );
};
