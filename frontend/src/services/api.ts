/**
 * Cliente HTTP da API REST do FoodPilot AI (`docs/contrato.md` v1.1.0).
 * Centraliza todas as chamadas aos endpoints `/api/v1/*` e o tratamento tipado de erros.
 */

import type {
  AiStatusResponse,
  ExecutiveReportResponse,
  HealthResponse,
  RecommendationsResponse,
  UploadItem,
  UploadListResponse,
  UploadMetricsResponse,
  ValidationErrorItem,
  ValidationErrorResponse,
} from '../types/api';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export function getApiBaseUrl(): string {
  const envUrl = import.meta.env?.VITE_API_BASE_URL;
  if (typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  return DEFAULT_API_BASE_URL;
}

/**
 * Exceção lançada quando a API retorna `400 Bad Request` ou `422 Unprocessable Entity`
 * na validação estrutural/domínio de um arquivo CSV (`RN-01`).
 */
export class ApiValidationError extends Error {
  public readonly status: number;
  public readonly detail: string;
  public readonly errors: ValidationErrorItem[];

  constructor(status: number, payload: ValidationErrorResponse) {
    super(payload.detail);
    this.name = 'ApiValidationError';
    this.status = status;
    this.detail = payload.detail;
    this.errors = Array.isArray(payload.errors) ? payload.errors : [];
  }
}

/**
 * Exceção lançada para outros códigos HTTP de erro (`404`, `500`, etc.).
 */
export class ApiHttpError extends Error {
  public readonly status: number;
  public readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiHttpError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * 2.1. Verificação de Saúde do Serviço (`GET /api/v1/health`)
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/health`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new ApiHttpError(
      response.status,
      'Serviço local da API indisponível no momento.'
    );
  }

  return (await response.json()) as HealthResponse;
}

/**
 * 2.3. Listagem de Uploads Realizados (`GET /api/v1/uploads`)
 */
export async function listUploads(): Promise<UploadListResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/uploads`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    let detail = 'Não foi possível carregar o histórico de lotes CSV.';
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Mantém mensagem amigável padrão se o corpo não for JSON válido
    }
    throw new ApiHttpError(response.status, detail);
  }

  return (await response.json()) as UploadListResponse;
}

/**
 * 2.2. Upload e Processamento de Lote CSV (`POST /api/v1/uploads`)
 */
export async function uploadOrdersCsv(file: File): Promise<UploadItem> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${getApiBaseUrl()}/api/v1/uploads`, {
    method: 'POST',
    body: formData,
  });

  if (response.status === 400 || response.status === 422) {
    let payload: ValidationErrorResponse = {
      detail: 'Arquivo CSV inválido: foram encontrados erros de validação.',
      errors: [],
    };
    try {
      const raw = (await response.json()) as Partial<ValidationErrorResponse>;
      payload = {
        detail:
          typeof raw.detail === 'string'
            ? raw.detail
            : 'Arquivo CSV inválido: foram encontrados erros de validação.',
        errors: Array.isArray(raw.errors) ? raw.errors : [],
      };
    } catch {
      // Preserva payload de fallback
    }
    throw new ApiValidationError(response.status, payload);
  }

  if (!response.ok) {
    let detail = 'Ocorreu um erro inesperado ao processar o arquivo CSV.';
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Ignora erro de parse JSON
    }
    throw new ApiHttpError(response.status, detail);
  }

  return (await response.json()) as UploadItem;
}

/**
 * 2.4. Consulta de Métricas Determinísticas do Lote (`GET /api/v1/uploads/{upload_id}/metrics`)
 */
export async function getUploadMetrics(
  uploadId: string
): Promise<UploadMetricsResponse> {
  const encodedId = encodeURIComponent(uploadId);
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/uploads/${encodedId}/metrics`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  if (!response.ok) {
    let detail = `Não foi possível carregar as métricas do lote '${uploadId}'.`;
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Ignora erro de parse JSON
    }
    throw new ApiHttpError(response.status, detail);
  }

  return (await response.json()) as UploadMetricsResponse;
}

/**
 * 2.5. Status do Agente de IA Local (`GET /api/v1/ai/status`)
 */
export async function getAiStatus(): Promise<AiStatusResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/ai/status`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response || !response.ok) {
    throw new ApiHttpError(
      response?.status ?? 503,
      'Não foi possível consultar o status do agente de IA local.'
    );
  }

  return (await response.json()) as AiStatusResponse;
}

/**
 * 2.6. Geração e Persistência de Recomendações Fundamentadas (`POST /api/v1/uploads/{upload_id}/recommendations`)
 */
export async function generateRecommendations(
  uploadId: string
): Promise<RecommendationsResponse> {
  const encodedId = encodeURIComponent(uploadId);
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/uploads/${encodedId}/recommendations`,
    {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  if (!response || !response.ok) {
    let detail = `Não foi possível gerar recomendações para o lote '${uploadId}'.`;
    try {
      const errBody = (await response?.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Ignora erro de parse JSON
    }
    throw new ApiHttpError(response?.status ?? 500, detail);
  }

  return (await response.json()) as RecommendationsResponse;
}

/**
 * 2.7. Consulta da Última Recomendação Gerada (`GET /api/v1/uploads/{upload_id}/recommendations`)
 * Retorna `null` quando a API responde `404 Not Found` (indicando que ainda não há recomendações geradas).
 */
export async function getRecommendations(
  uploadId: string
): Promise<RecommendationsResponse | null> {
  const encodedId = encodeURIComponent(uploadId);
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/uploads/${encodedId}/recommendations`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  if (!response || response.status === 404) {
    return null;
  }

  if (!response.ok) {
    let detail = `Não foi possível consultar as recomendações do lote '${uploadId}'.`;
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Ignora erro de parse JSON
    }
    throw new ApiHttpError(response.status, detail);
  }

  return (await response.json()) as RecommendationsResponse;
}

/**
 * 2.8. Consulta do Relatório Executivo Consolidado (`GET /api/v1/uploads/{upload_id}/report`)
 */
export async function getExecutiveReport(
  uploadId: string
): Promise<ExecutiveReportResponse> {
  const encodedId = encodeURIComponent(uploadId);
  const response = await fetch(
    `${getApiBaseUrl()}/api/v1/uploads/${encodedId}/report`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  if (!response.ok) {
    let detail = `Não foi possível gerar o relatório executivo do lote '${uploadId}'.`;
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (typeof errBody?.detail === 'string') {
        detail = errBody.detail;
      }
    } catch {
      // Ignora erro de parse JSON
    }
    throw new ApiHttpError(response.status, detail);
  }

  return (await response.json()) as ExecutiveReportResponse;
}



