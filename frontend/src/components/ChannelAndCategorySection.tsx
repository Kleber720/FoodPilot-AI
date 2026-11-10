import React, { useState } from 'react';
import type { CategoryBreakdownItem, ChannelBreakdownItem } from '../types/api';
import {
  formatChannelLabel,
  formatCurrencyBRL,
  formatMinutes,
  formatPercent,
} from '../utils/formatters';

export interface ChannelAndCategorySectionProps {
  byChannel: ChannelBreakdownItem[];
  byCategory: CategoryBreakdownItem[];
}

export const ChannelAndCategorySection: React.FC<ChannelAndCategorySectionProps> = ({
  byChannel,
  byCategory,
}) => {
  const [selectedChannel, setSelectedChannel] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const visibleChannels =
    selectedChannel === 'ALL'
      ? byChannel
      : byChannel.filter((item) => item.channel === selectedChannel);

  const visibleCategories =
    selectedCategory === 'ALL'
      ? byCategory
      : byCategory.filter((item) => item.category === selectedCategory);

  return (
    <div className="split-grid">
      {/* Desempenho por Canal */}
      <section className="panel-card" aria-labelledby="channel-breakdown-heading">
        <div className="section-header">
          <div>
            <h2 id="channel-breakdown-heading" className="section-title">
              Desempenho por Canal de Venda
            </h2>
            <p className="section-subtitle">
              Receita líquida, participação e ticket médio por canal (pedidos concluídos).
            </p>
          </div>

          <div className="filter-group" role="group" aria-label="Filtrar por canal de venda">
            <span className="filter-label">Canal:</span>
            <button
              type="button"
              className="filter-pill"
              aria-pressed={selectedChannel === 'ALL'}
              onClick={() => setSelectedChannel('ALL')}
            >
              Todos Canais
            </button>
            {byChannel.map((ch) => (
              <button
                key={ch.channel}
                type="button"
                className="filter-pill"
                aria-pressed={selectedChannel === ch.channel}
                onClick={() => setSelectedChannel(ch.channel)}
              >
                {formatChannelLabel(ch.channel)} ({ch.channel})
              </button>
            ))}
          </div>
        </div>

        {visibleChannels.length === 0 ? (
          <div className="alert-box alert-box--info" role="status">
            Nenhum canal encontrado para o filtro selecionado.
          </div>
        ) : (
          <>
            <div className="pareto-chart" aria-label="Participação de receita líquida por canal">
              {visibleChannels.map((ch) => (
                <div key={ch.channel} className="pareto-row">
                  <div className="pareto-label">
                    <strong>{formatChannelLabel(ch.channel)}</strong>
                    <code>({ch.channel})</code>
                  </div>
                  <div className="pareto-track">
                    <div
                      className="pareto-bar pareto-bar--channel"
                      style={{ width: `${Math.min(100, Math.max(2, ch.revenue_share_pct))}%` }}
                    />
                  </div>
                  <div className="pareto-metrics">
                    <strong>{formatPercent(ch.revenue_share_pct)}</strong> ({formatCurrencyBRL(ch.net_revenue)})
                  </div>
                </div>
              ))}
            </div>

            <div className="table-container">
              <table className="data-table" aria-label="Tabela de desempenho por canal">
                <thead>
                  <tr>
                    <th scope="col">Canal</th>
                    <th scope="col" className="num-col">
                      Pedidos Válidos
                    </th>
                    <th scope="col" className="num-col">
                      Itens
                    </th>
                    <th scope="col" className="num-col">
                      Fat. Bruto
                    </th>
                    <th scope="col" className="num-col">
                      Descontos
                    </th>
                    <th scope="col" className="num-col">
                      Fat. Líquido
                    </th>
                    <th scope="col" className="num-col">
                      Ticket Médio Líq.
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {visibleChannels.map((ch) => (
                    <tr key={ch.channel}>
                      <td>
                        <strong>{formatChannelLabel(ch.channel)}</strong> <code>{ch.channel}</code>
                      </td>
                      <td className="num-col">{ch.valid_orders_count}</td>
                      <td className="num-col">{ch.quantity_sold}</td>
                      <td className="num-col">{formatCurrencyBRL(ch.gross_revenue)}</td>
                      <td className="num-col">{formatCurrencyBRL(ch.discount_total)}</td>
                      <td className="num-col">{formatCurrencyBRL(ch.net_revenue)}</td>
                      <td className="num-col">{formatCurrencyBRL(ch.average_ticket_net)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>

      {/* Desempenho por Categoria */}
      <section className="panel-card" aria-labelledby="category-breakdown-heading">
        <div className="section-header">
          <div>
            <h2 id="category-breakdown-heading" className="section-title">
              Desempenho por Categoria do Cardápio
            </h2>
            <p className="section-subtitle">
              Volume vendido, receita líquida e tempo médio de preparo por categoria.
            </p>
          </div>

          <div className="filter-group" role="group" aria-label="Filtrar por categoria do cardápio">
            <span className="filter-label">Categoria:</span>
            <button
              type="button"
              className="filter-pill"
              aria-pressed={selectedCategory === 'ALL'}
              onClick={() => setSelectedCategory('ALL')}
            >
              Todas Categorias
            </button>
            {byCategory.map((cat) => (
              <button
                key={cat.category}
                type="button"
                className="filter-pill"
                aria-pressed={selectedCategory === cat.category}
                onClick={() => setSelectedCategory(cat.category)}
              >
                {cat.category}
              </button>
            ))}
          </div>
        </div>

        {visibleCategories.length === 0 ? (
          <div className="alert-box alert-box--info" role="status">
            Nenhuma categoria encontrada para o filtro selecionado.
          </div>
        ) : (
          <>
            <div className="pareto-chart" aria-label="Participação de receita líquida por categoria">
              {visibleCategories.map((cat) => (
                <div key={cat.category} className="pareto-row">
                  <div className="pareto-label">
                    <strong>{cat.category}</strong>
                  </div>
                  <div className="pareto-track">
                    <div
                      className="pareto-bar pareto-bar--channel"
                      style={{ width: `${Math.min(100, Math.max(2, cat.revenue_share_pct))}%` }}
                    />
                  </div>
                  <div className="pareto-metrics">
                    <strong>{formatPercent(cat.revenue_share_pct)}</strong> ({formatCurrencyBRL(cat.net_revenue)})
                  </div>
                </div>
              ))}
            </div>

            <div className="table-container">
              <table className="data-table" aria-label="Tabela de desempenho por categoria">
                <thead>
                  <tr>
                    <th scope="col">Categoria</th>
                    <th scope="col" className="num-col">
                      Qtd. Vendida
                    </th>
                    <th scope="col" className="num-col">
                      Fat. Bruto
                    </th>
                    <th scope="col" className="num-col">
                      Descontos
                    </th>
                    <th scope="col" className="num-col">
                      Fat. Líquido
                    </th>
                    <th scope="col" className="num-col">
                      Preparo Médio
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {visibleCategories.map((cat) => (
                    <tr key={cat.category}>
                      <td>
                        <strong>{cat.category}</strong>
                      </td>
                      <td className="num-col">{cat.quantity_sold}</td>
                      <td className="num-col">{formatCurrencyBRL(cat.gross_revenue)}</td>
                      <td className="num-col">{formatCurrencyBRL(cat.discount_total)}</td>
                      <td className="num-col">{formatCurrencyBRL(cat.net_revenue)}</td>
                      <td className="num-col">{formatMinutes(cat.average_prep_time_minutes)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
};
