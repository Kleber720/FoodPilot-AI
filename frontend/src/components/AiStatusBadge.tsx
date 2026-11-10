import React from 'react';
import type { AiStatusResponse } from '../types/api';

export interface AiStatusBadgeProps {
  aiStatus: AiStatusResponse | null;
  isChecking?: boolean;
  onRefresh?: () => void;
}

/**
 * Exibe no cabeçalho executivo o estado do servidor local Ollama (`GET /api/v1/ai/status` — §2.5).
 */
export const AiStatusBadge: React.FC<AiStatusBadgeProps> = ({
  aiStatus,
  isChecking = false,
  onRefresh,
}) => {
  if (isChecking) {
    return (
      <span className="badge badge-info" role="status" data-testid="ai-status-badge">
        IA Local: Verificando...
      </span>
    );
  }

  if (aiStatus && aiStatus.ollama_reachable && aiStatus.model_available) {
    return (
      <span
        className="badge badge-success"
        role="status"
        data-testid="ai-status-badge"
        title={`Servidor Ollama ativo em ${aiStatus.base_url}`}
      >
        IA Local ({aiStatus.model}): Online
      </span>
    );
  }

  if (aiStatus && aiStatus.ollama_reachable && !aiStatus.model_available) {
    return (
      <span
        className="badge badge-warning"
        role="status"
        data-testid="ai-status-badge"
        title={`Servidor Ollama acessível em ${aiStatus.base_url}, mas o modelo ${aiStatus.model} não foi encontrado`}
        onClick={onRefresh}
      >
        IA Local ({aiStatus.model}): Modelo ausente (Fallback Determinístico Ativo)
      </span>
    );
  }

  return (
    <span
      className="badge badge-warning"
      role="status"
      data-testid="ai-status-badge"
      title="Servidor Ollama inacessível; o sistema utiliza automaticamente o motor determinístico (RN-09)"
      onClick={onRefresh}
    >
      IA Local: Offline (Fallback Determinístico Ativo)
    </span>
  );
};
