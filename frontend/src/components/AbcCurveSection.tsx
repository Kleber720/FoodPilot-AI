import React, { useState } from 'react';
import type { ABCClass, ABCCurveItem } from '../types/api';
import { formatCurrencyBRL, formatPercent } from '../utils/formatters';

export interface AbcCurveSectionProps {
  abcCurve: ABCCurveItem[];
}

type AbcFilterOption = 'ALL' | ABCClass;

export const AbcCurveSection: React.FC<AbcCurveSectionProps> = ({ abcCurve }) => {
  const [selectedClass, setSelectedClass] = useState<AbcFilterOption>('ALL');

  const filteredItems =
    selectedClass === 'ALL'
      ? abcCurve
      : abcCurve.filter((item) => item.abc_class === selectedClass);

  const filterButtons: { label: string; value: AbcFilterOption }[] = [
    { label: 'Todas', value: 'ALL' },
    { label: 'Classe A', value: 'A' },
    { label: 'Classe B', value: 'B' },
    { label: 'Classe C', value: 'C' },
  ];

  return (
    <section className="panel-card" aria-labelledby="abc-curve-heading">
      <div className="section-header">
        <div>
          <h2 id="abc-curve-heading" className="section-title">
            Curva ABC de Produtos (Pareto — RN-05)
          </h2>
          <p className="section-subtitle">
            Classificação determinística por receita bruta: Classe A (até 80%), Classe B (80% a 95%) e Classe C (&gt; 95%).
          </p>
        </div>

        <div className="filter-group" role="group" aria-label="Filtrar Curva ABC por classe">
          <span className="filter-label">Classe ABC:</span>
          {filterButtons.map((btn) => (
            <button
              key={btn.value}
              type="button"
              className="filter-pill"
              aria-pressed={selectedClass === btn.value}
              onClick={() => setSelectedClass(btn.value)}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {abcCurve.length === 0 ? (
        <div className="alert-box alert-box--info" role="status">
          Nenhum produto concluído disponível para compor a Curva ABC neste lote.
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="alert-box alert-box--info" role="status">
          <p style={{ margin: '0 0 0.5rem' }}>
            Nenhum produto encontrado na <strong>Classe {selectedClass}</strong> para este lote.
          </p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setSelectedClass('ALL')}
          >
            Mostrar todas as classes
          </button>
        </div>
      ) : (
        <>
          <div className="pareto-chart" aria-label="Gráfico visual de Pareto da Curva ABC">
            {filteredItems.map((item) => (
              <div key={item.item_name} className="pareto-row">
                <div className="pareto-label">
                  <span className={`badge badge-abc-${item.abc_class}`}>
                    Classe {item.abc_class}
                  </span>
                  <span>{item.item_name}</span>
                </div>
                <div
                  className="pareto-track"
                  role="progressbar"
                  aria-valuenow={item.revenue_share_pct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Participação de ${item.item_name}: ${formatPercent(item.revenue_share_pct)}`}
                >
                  <div
                    className={`pareto-bar pareto-bar--${item.abc_class}`}
                    style={{ width: `${Math.min(100, Math.max(2, item.revenue_share_pct))}%` }}
                  />
                </div>
                <div className="pareto-metrics">
                  <strong>{formatPercent(item.revenue_share_pct)}</strong> (Acum.:{' '}
                  {formatPercent(item.cumulative_share_pct)})
                </div>
              </div>
            ))}
          </div>

          <div className="table-container">
            <table className="data-table" aria-label="Tabela da Curva ABC de produtos">
              <caption>
                Exibindo {filteredItems.length} de {abcCurve.length} produtos classificados
              </caption>
              <thead>
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Produto</th>
                  <th scope="col">Categoria</th>
                  <th scope="col" className="num-col">
                    Qtd. Vendida
                  </th>
                  <th scope="col" className="num-col">
                    Receita Bruta
                  </th>
                  <th scope="col" className="num-col">
                    Part. Individual (%)
                  </th>
                  <th scope="col" className="num-col">
                    Part. Acumulada (%)
                  </th>
                  <th scope="col">Classe ABC</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => {
                  const originalRank =
                    abcCurve.findIndex((orig) => orig.item_name === item.item_name) + 1;
                  return (
                    <tr key={item.item_name}>
                      <td className="num-col">{originalRank}</td>
                      <td>
                        <strong>{item.item_name}</strong>
                      </td>
                      <td>{item.category}</td>
                      <td className="num-col">{item.quantity_sold}</td>
                      <td className="num-col">{formatCurrencyBRL(item.revenue)}</td>
                      <td className="num-col">{formatPercent(item.revenue_share_pct)}</td>
                      <td className="num-col">{formatPercent(item.cumulative_share_pct)}</td>
                      <td>
                        <span className={`badge badge-abc-${item.abc_class}`}>
                          Classe {item.abc_class}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
};
