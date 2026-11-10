import React, { useCallback, useEffect, useState } from 'react';
import { AbcCurveSection } from './components/AbcCurveSection';
import { AiStatusBadge } from './components/AiStatusBadge';
import { BottlenecksAndAnomaliesSection } from './components/BottlenecksAndAnomaliesSection';
import { ChannelAndCategorySection } from './components/ChannelAndCategorySection';
import { FinancialKpiGrid } from './components/FinancialKpiGrid';
import { RecommendationsPanel } from './components/RecommendationsPanel';
import { UploadHistorySelector } from './components/UploadHistorySelector';
import { UploadPanel } from './components/UploadPanel';
import {
  ApiHttpError,
  checkHealth,
  generateRecommendations,
  getAiStatus,
  getExecutiveReport,
  getRecommendations,
  getUploadMetrics,
  listUploads,
} from './services/api';
import type {
  AiStatusResponse,
  ExecutiveReportResponse,
  RecommendationsResponse,
  UploadItem,
  UploadMetricsResponse,
} from './types/api';

export const App: React.FC = () => {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [totalUploads, setTotalUploads] = useState<number>(0);
  const [selectedUploadId, setSelectedUploadId] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<UploadMetricsResponse | null>(null);

  // Estados de IA e Recomendações (RN-07 a RN-10)
  const [aiStatus, setAiStatus] = useState<AiStatusResponse | null>(null);
  const [isCheckingAi, setIsCheckingAi] = useState<boolean>(false);
  const [recommendations, setRecommendations] = useState<RecommendationsResponse | null>(null);
  const [isLoadingRecsInitial, setIsLoadingRecsInitial] = useState<boolean>(false);
  const [isGeneratingRecs, setIsGeneratingRecs] = useState<boolean>(false);
  const [recsError, setRecsError] = useState<string | null>(null);

  // Estados de Relatório Executivo (Entrega 0004)
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);
  const [reportData, setReportData] = useState<ExecutiveReportResponse | null>(null);
  const [isLoadingReport, setIsLoadingReport] = useState<boolean>(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);

  const [isLoadingInitial, setIsLoadingInitial] = useState<boolean>(true);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState<boolean>(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [apiHealthStatus, setApiHealthStatus] = useState<'ok' | 'offline' | 'checking'>('ok');

  const checkAiHealth = useCallback(async () => {
    setIsCheckingAi(true);
    try {
      const statusRes = await getAiStatus();
      setAiStatus(statusRes);
    } catch {
      setAiStatus({
        ollama_reachable: false,
        base_url: 'http://localhost:11434',
        model: 'qwen3:4b-instruct',
        model_available: false,
      });
    } finally {
      setIsCheckingAi(false);
    }
  }, []);

  const loadRecommendationsForUpload = useCallback(async (uploadId: string) => {
    setIsLoadingRecsInitial(true);
    setRecsError(null);
    try {
      const recsRes = await getRecommendations(uploadId);
      setRecommendations(recsRes);
    } catch (err) {
      if (err instanceof ApiHttpError) {
        setRecsError(err.detail);
      } else {
        setRecsError('Não foi possível carregar as recomendações para este lote.');
      }
    } finally {
      setIsLoadingRecsInitial(false);
    }
  }, []);

  const loadMetricsForUpload = useCallback(async (uploadId: string) => {
    setIsLoadingMetrics(true);
    setGlobalError(null);
    try {
      const metricsResponse = await getUploadMetrics(uploadId);
      setMetrics(metricsResponse);
      setApiHealthStatus('ok');
    } catch (err) {
      if (err instanceof ApiHttpError) {
        setGlobalError(err.detail);
      } else {
        setGlobalError(
          'Não foi possível carregar as métricas do lote selecionado. Verifique a conexão com a API local.'
        );
      }
    } finally {
      setIsLoadingMetrics(false);
    }
  }, []);

  const loadInitialUploads = useCallback(async () => {
    setIsLoadingInitial(true);
    setGlobalError(null);
    try {
      void checkAiHealth();
      const listResponse = await listUploads();
      setUploads(listResponse.items);
      setTotalUploads(listResponse.total);
      setApiHealthStatus('ok');

      if (listResponse.items.length > 0) {
        const firstUploadId = listResponse.items[0].upload_id;
        setSelectedUploadId(firstUploadId);
        await Promise.all([
          loadMetricsForUpload(firstUploadId),
          loadRecommendationsForUpload(firstUploadId),
        ]);
      } else {
        setSelectedUploadId(null);
        setMetrics(null);
        setRecommendations(null);
      }
    } catch (err) {
      setApiHealthStatus('offline');
      if (err instanceof ApiHttpError) {
        setGlobalError(err.detail);
      } else {
        setGlobalError(
          'Não foi possível conectar ao servidor local da API (http://localhost:8000).'
        );
      }
    } finally {
      setIsLoadingInitial(false);
    }
  }, [checkAiHealth, loadMetricsForUpload, loadRecommendationsForUpload]);

  useEffect(() => {
    void loadInitialUploads();
  }, [loadInitialUploads]);

  const handleSelectUpload = async (uploadId: string) => {
    setSelectedUploadId(uploadId);
    await Promise.all([
      loadMetricsForUpload(uploadId),
      loadRecommendationsForUpload(uploadId),
    ]);
  };

  const handleUploadSuccess = async (uploadedItem: UploadItem) => {
    setUploads((prev) => {
      const withoutDuplicate = prev.filter((item) => item.upload_id !== uploadedItem.upload_id);
      const updated = [uploadedItem, ...withoutDuplicate];
      setTotalUploads(updated.length);
      return updated;
    });
    setSelectedUploadId(uploadedItem.upload_id);
    await Promise.all([
      loadMetricsForUpload(uploadedItem.upload_id),
      loadRecommendationsForUpload(uploadedItem.upload_id),
    ]);
  };

  const handleVerifyHealth = async () => {
    setApiHealthStatus('checking');
    try {
      const res = await checkHealth();
      setApiHealthStatus(res.status === 'ok' ? 'ok' : 'offline');
    } catch {
      setApiHealthStatus('offline');
    }
    void checkAiHealth();
  };

  const handleGenerateRecommendations = async () => {
    if (!selectedUploadId) return;
    setIsGeneratingRecs(true);
    setRecsError(null);
    try {
      const newRecs = await generateRecommendations(selectedUploadId);
      setRecommendations(newRecs);
    } catch (err) {
      if (err instanceof ApiHttpError) {
        setRecsError(err.detail);
      } else {
        setRecsError('Erro ao gerar novas recomendações. O sistema ativou o fallback se necessário.');
      }
    } finally {
      setIsGeneratingRecs(false);
    }
  };

  const handleOpenReport = async () => {
    if (!selectedUploadId) return;
    setIsLoadingReport(true);
    setIsReportModalOpen(true);
    setCopyFeedback(null);
    try {
      const report = await getExecutiveReport(selectedUploadId);
      setReportData(report);
    } catch (err) {
      if (err instanceof ApiHttpError) {
        setGlobalError(err.detail);
      }
    } finally {
      setIsLoadingReport(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopyMarkdown = async () => {
    if (!reportData?.report_markdown) return;
    try {
      await navigator.clipboard.writeText(reportData.report_markdown);
      setCopyFeedback('Copiado para a área de transferência!');
      setTimeout(() => setCopyFeedback(null), 3000);
    } catch {
      setCopyFeedback('Não foi possível copiar automaticamente.');
    }
  };

  const activeUpload = uploads.find((u) => u.upload_id === selectedUploadId);
  const activeUploadSummary = activeUpload?.summary_metrics ?? null;
  const activeFilename = activeUpload?.filename ?? 'Lote Atual';

  return (
    <div className="app-shell">
      {/* Cabeçalho impresso exclusivo para PDF/Papel */}
      <div className="print-only" aria-hidden="true">
        <h1 style={{ margin: 0, fontSize: '18pt' }}>FoodPilot AI — Relatório Executivo de Vendas e Operação</h1>
        <p style={{ margin: '0.25rem 0', fontSize: '9pt', color: '#475569' }}>
          Restaurante Demo • Lote: <strong>{activeFilename}</strong> • Gerado em: {new Date().toLocaleString('pt-BR')}
        </p>
      </div>

      <header className="app-header">
        <div className="app-brand">
          <h1>
            <span className="brand-badge" aria-hidden="true">🍔</span>
            FoodPilot AI — Dashboard Operacional e Financeiro
          </h1>
          <p>
            Inteligência determinística para restaurantes • Processamento local em Python + pandas + SQLite + Ollama
          </p>
        </div>

        <div className="header-badges">
          <AiStatusBadge
            aiStatus={aiStatus}
            isChecking={isCheckingAi}
            onRefresh={checkAiHealth}
          />
          <span
            className={`badge ${
              apiHealthStatus === 'ok'
                ? 'badge-success'
                : apiHealthStatus === 'checking'
                  ? 'badge-info'
                  : 'badge-critical'
            }`}
            role="status"
          >
            API Local: {apiHealthStatus === 'ok' ? 'Online (OK)' : apiHealthStatus === 'checking' ? 'Verificando...' : 'Indisponível'}
          </span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleVerifyHealth}
            title="Verificar disponibilidade em GET /api/v1/health e status da IA"
          >
            Verificar API / IA
          </button>
          {metrics && selectedUploadId && (
            <>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handlePrint}
                title="Imprimir ou Salvar em PDF"
                data-testid="btn-print-report"
              >
                🖨️ Imprimir / PDF
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleOpenReport}
                title="Ver Relatório Executivo Consolidado"
                data-testid="btn-open-report"
              >
                📄 Relatório Executivo
              </button>
            </>
          )}
        </div>
      </header>

      <main style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="ingestion-grid">
          <UploadPanel onUploadSuccess={handleUploadSuccess} />
          <UploadHistorySelector
            uploads={uploads}
            total={totalUploads}
            selectedUploadId={selectedUploadId}
            isLoadingMetrics={isLoadingMetrics}
            onSelectUpload={handleSelectUpload}
          />
        </div>

        {globalError && (
          <div className="alert-box alert-box--error" role="alert">
            <p className="alert-title">Falha de comunicação ou consulta</p>
            <p style={{ margin: '0 0 0.75rem' }}>{globalError}</p>
            <button type="button" className="btn btn-secondary" onClick={loadInitialUploads}>
              Tentar novamente
            </button>
          </div>
        )}

        {isLoadingInitial ? (
          <div className="panel-card" role="status" aria-live="polite" aria-busy="true">
            <p style={{ margin: 0, fontWeight: 600 }}>
              Carregando histórico de lotes e métricas do FoodPilot AI...
            </p>
          </div>
        ) : totalUploads === 0 && !metrics ? (
          <section className="empty-state" aria-label="Estado vazio do dashboard">
            <h2>Bem-vindo ao FoodPilot AI</h2>
            <p>
              Ainda não há lotes de vendas importados no banco SQLite local. Envie um arquivo{' '}
              <code>.csv</code> no painel acima para visualizar automaticamente o Faturamento Bruto,
              Faturamento Líquido, Ticket Médio, Curva ABC (Pareto), Canais, Gargalos Operacionais e
              as Recomendações Práticas da IA.
            </p>
          </section>
        ) : isLoadingMetrics ? (
          <div className="panel-card" role="status" aria-live="polite" aria-busy="true">
            <p style={{ margin: 0, fontWeight: 600 }}>
              Carregando relatório determinístico de métricas do lote selecionado...
            </p>
          </div>
        ) : metrics && selectedUploadId ? (
          <>
            <FinancialKpiGrid
              financials={metrics.financials}
              totalRows={metrics.total_rows}
              topAbcItem={activeUploadSummary?.top_abc_item}
            />

            <AbcCurveSection abcCurve={metrics.abc_curve} />

            <ChannelAndCategorySection
              byChannel={metrics.by_channel}
              byCategory={metrics.by_category}
            />

            <BottlenecksAndAnomaliesSection bottlenecks={metrics.bottlenecks} />

            <RecommendationsPanel
              uploadId={selectedUploadId}
              filename={activeFilename}
              recommendations={recommendations}
              isLoadingInitial={isLoadingRecsInitial}
              isGenerating={isGeneratingRecs}
              error={recsError}
              onGenerate={handleGenerateRecommendations}
            />
          </>
        ) : null}
      </main>

      {/* Modal de Relatório Executivo Consolidado */}
      {isReportModalOpen && (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-report-title">
          <div className="modal-card">
            <div className="modal-header">
              <h3 id="modal-report-title" style={{ margin: 0 }}>
                Relatório Executivo Consolidado — {activeFilename}
              </h3>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsReportModalOpen(false)}
                aria-label="Fechar modal"
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              {isLoadingReport ? (
                <p>Gerando e formatando visão executiva do lote...</p>
              ) : reportData ? (
                <div>
                  <p style={{ margin: '0 0 1rem', color: 'var(--color-text-secondary)' }}>
                    Origem da Análise:{' '}
                    <strong>
                      {reportData.recommendations_source === 'llm' || reportData.recommendations_source === 'ollama'
                        ? 'Agente de IA Local (qwen3:4b-instruct)'
                        : 'Regras Determinísticas de Contingência (Fallback)'}
                    </strong>
                  </p>
                  <pre className="report-markdown-preview">
                    {reportData.report_markdown}
                  </pre>
                  {copyFeedback && (
                    <p style={{ color: 'var(--color-success-text)', fontWeight: 600, marginTop: '0.5rem' }}>
                      {copyFeedback}
                    </p>
                  )}
                </div>
              ) : (
                <p>Não foi possível carregar o relatório executivo.</p>
              )}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCopyMarkdown}
                disabled={!reportData}
              >
                📋 Copiar Markdown
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handlePrint}
              >
                🖨️ Imprimir / PDF
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setIsReportModalOpen(false)}
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
