import React, { useState } from 'react';
import { ApiHttpError, ApiValidationError, uploadOrdersCsv } from '../services/api';
import type { UploadItem, ValidationErrorItem } from '../types/api';

export interface UploadPanelProps {
  onUploadSuccess: (uploadedItem: UploadItem) => Promise<void> | void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationErrorItem[]>([]);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setErrorDetail(null);
    setValidationErrors([]);
    setSuccessMessage(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorDetail(null);
    setValidationErrors([]);
    setSuccessMessage(null);

    if (!selectedFile) {
      setErrorDetail('Selecione um arquivo CSV de pedidos antes de enviar.');
      return;
    }

    setIsSubmitting(true);
    try {
      const uploaded = await uploadOrdersCsv(selectedFile);
      setSuccessMessage(
        `Lote "${uploaded.filename}" processado com sucesso (${uploaded.total_rows} linhas, ${uploaded.valid_orders_count} pedidos concluídos).`
      );
      await onUploadSuccess(uploaded);
    } catch (err) {
      if (err instanceof ApiValidationError) {
        setErrorDetail(err.detail);
        setValidationErrors(err.errors);
      } else if (err instanceof ApiHttpError) {
        setErrorDetail(err.detail);
      } else {
        setErrorDetail(
          'Falha de conexão com a API local. Verifique se o servidor FastAPI está em execução.'
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="panel-card" aria-labelledby="upload-panel-heading">
      <div className="section-header">
        <div>
          <h2 id="upload-panel-heading" className="section-title">
            Importar Lote de Pedidos (CSV)
          </h2>
          <p className="section-subtitle">
            Envie um arquivo CSV UTF-8 com as 10 colunas obrigatórias para validação atômica (RN-01 / RN-02).
          </p>
        </div>
        <span className="badge badge-info">POST /api/v1/uploads</span>
      </div>

      <form onSubmit={handleSubmit} noValidate aria-busy={isSubmitting}>
        <div className="form-field">
          <label htmlFor="csv-upload-input" className="form-label">
            Arquivo CSV de pedidos
          </label>
          <input
            id="csv-upload-input"
            name="file"
            type="file"
            accept=".csv,text/csv"
            className="file-input"
            onChange={handleFileChange}
            disabled={isSubmitting}
            aria-describedby="csv-upload-hint"
          />
          <p id="csv-upload-hint" className="field-hint">
            Colunas exigidas: <code>order_id</code>, <code>timestamp</code>, <code>item_name</code>,{' '}
            <code>category</code>, <code>quantity</code>, <code>unit_price</code>, <code>discount</code>,{' '}
            <code>prep_time_minutes</code>, <code>status</code>, <code>channel</code>.
          </p>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Processando lote CSV...' : 'Enviar e Processar CSV'}
        </button>
      </form>

      {successMessage && (
        <div className="alert-box alert-box--success" role="status" aria-live="polite">
          <p className="alert-title">Importação concluída</p>
          <p style={{ margin: 0 }}>{successMessage}</p>
        </div>
      )}

      {errorDetail && (
        <div className="alert-box alert-box--error" role="alert" aria-live="assertive">
          <p className="alert-title">{errorDetail}</p>
          <p style={{ margin: '0 0 0.75rem', fontSize: '0.875rem' }}>
            Pela regra de atomicidade (RN-02), nenhum registro foi gravado no banco. Corrija os itens abaixo e envie novamente:
          </p>

          {validationErrors.length > 0 && (
            <div className="table-container" style={{ backgroundColor: 'var(--color-surface)' }}>
              <table className="data-table" aria-label="Erros de validação do arquivo CSV">
                <thead>
                  <tr>
                    <th scope="col">Linha</th>
                    <th scope="col">Coluna</th>
                    <th scope="col">Mensagem de Validação</th>
                  </tr>
                </thead>
                <tbody>
                  {validationErrors.map((errItem, idx) => (
                    <tr key={`${errItem.row ?? 'header'}-${errItem.column ?? 'all'}-${idx}`}>
                      <td className="num-col">
                        {errItem.row !== null ? errItem.row : 'Cabeçalho / Arquivo'}
                      </td>
                      <td>
                        <code>{errItem.column !== null ? errItem.column : 'Geral'}</code>
                      </td>
                      <td>{errItem.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
