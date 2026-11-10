/**
 * Utilitários puros de formatação visual para o Dashboard do FoodPilot AI.
 * Nenhuma função altera ou recalcula regras de negócio; apenas formata valores já recebidos da API.
 */

import type { EvidenceUnit, RecommendationTheme } from '../types/api';

const brlFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Formata valor numérico para moeda BRL (`R$ 5.000,00`) normalizando espaço não-quebrável.
 */
export function formatCurrencyBRL(value: number): string {
  return brlFormatter.format(value).replace(/\u00a0/g, ' ');
}

/**
 * Formata percentual com 2 casas decimais no padrão brasileiro (ex.: `59,44%` ou `40,00%`).
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(2).replace('.', ',')}%`;
}

/**
 * Formata tempo em minutos (ex.: `21,4 min`).
 */
export function formatMinutes(value: number): string {
  return `${Number(value.toFixed(2)).toString().replace('.', ',')} min`;
}

/**
 * Formata timestamp ISO-8601 UTC para exibição legível em pt-BR.
 */
export function formatDateTimeUTC(isoString: string): string {
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return isoString;
  }
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
    timeZone: 'UTC',
  }).format(parsed);
}

/**
 * Rótulo amigável para os canais de venda do domínio (`balcao`, `delivery`, `app`).
 */
export function formatChannelLabel(channel: string): string {
  switch (channel) {
    case 'delivery':
      return 'Delivery';
    case 'app':
      return 'App Próprio';
    case 'balcao':
      return 'Balcão / Salão';
    default:
      return channel;
  }
}

/**
 * Formata o valor oficial de uma evidência (`evidence[].value`) de acordo com sua unidade (`unit`)
 * sem qualquer recálculo ou extração de texto (`RN-08`).
 */
export function formatEvidenceValue(value: number, unit: EvidenceUnit): string {
  switch (unit) {
    case 'BRL':
      return formatCurrencyBRL(value);
    case '%':
      return formatPercent(value);
    case 'min':
      return formatMinutes(value);
    case 'count':
    default:
      return `${Math.round(value)}`;
  }
}

/**
 * Rótulo legível para o tema da recomendação (`RN-10`).
 */
export function formatThemeLabel(theme: RecommendationTheme): string {
  switch (theme) {
    case 'delivery':
      return 'Canais e Delivery';
    case 'prep_time':
      return 'Tempo de Preparo e Gargalos';
    case 'mix_products':
      return 'Mix de Produtos e Curva ABC';
    case 'cancelamento':
      return 'Cancelamento';
    case 'operacao':
      return 'Operação e Cozinha';
    case 'mix':
      return 'Mix e Curva ABC';
    case 'receita':
      return 'Receita e Ticket';
    default:
      return theme;
  }
}
