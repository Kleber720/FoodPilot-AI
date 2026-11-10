"""
Gera um dataset de pedidos simulados para uma Pizzaria Artesanal (data/pizzeria_sample_orders.csv).
Projetado para validar a flexibilidade do FoodPilot AI com novo mix de produtos, canais e horários de pico.
"""

import io
from pathlib import Path
import sys

# Garante que a raiz do projeto esteja no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from data_pipeline import validate_and_parse_csv, calculate_metrics

orders_data = [
    # Sexta-feira Noite - 07/11/2026
    # ORD-101: Balcão - Jantar Casal
    ("ORD-101", "2026-11-07T19:10:00Z", "Burrata com Pesto e Focaccia", "Entradas", 1, 58.00, 0.00, 12.0, "completed", "balcao"),
    ("ORD-101", "2026-11-07T19:10:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 0.00, 22.0, "completed", "balcao"),
    ("ORD-101", "2026-11-07T19:10:00Z", "Vinho Chianti Reserva Taca", "Bebidas", 2, 34.00, 8.00, 4.0, "completed", "balcao"),

    # ORD-102: Delivery - Família
    ("ORD-102", "2026-11-07T19:25:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 10.00, 36.0, "completed", "delivery"),
    ("ORD-102", "2026-11-07T19:25:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 0.00, 32.0, "completed", "delivery"),
    ("ORD-102", "2026-11-07T19:25:00Z", "Refrigerante 2L Guarana", "Bebidas", 1, 16.00, 0.00, 2.0, "completed", "delivery"),

    # ORD-103: App iFood - Jantar Individual
    ("ORD-103", "2026-11-07T19:40:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 5.00, 25.0, "completed", "app"),
    ("ORD-103", "2026-11-07T19:40:00Z", "Cerveja Artesanal IPA 500ml", "Bebidas", 1, 26.00, 0.00, 3.0, "completed", "app"),

    # ORD-104: Delivery - Pico de Atraso no Forno
    ("ORD-104", "2026-11-07T20:00:00Z", "Pizza Parma & Rucola", "Pizzas", 2, 94.00, 15.00, 48.0, "completed", "delivery"),
    ("ORD-104", "2026-11-07T20:00:00Z", "Crostini Gorgonzola e Mel", "Entradas", 1, 42.00, 0.00, 16.0, "completed", "delivery"),

    # ORD-105: Delivery - Cancelado por Demora
    ("ORD-105", "2026-11-07T20:15:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 2, 88.00, 0.00, 55.0, "canceled", "delivery"),
    ("ORD-105", "2026-11-07T20:15:00Z", "Refrigerante 2L Guarana", "Bebidas", 1, 16.00, 0.00, 2.0, "canceled", "delivery"),

    # ORD-106: Balcão
    ("ORD-106", "2026-11-07T20:30:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 10.00, 24.0, "completed", "balcao"),
    ("ORD-106", "2026-11-07T20:30:00Z", "Tiramisu Tradicional", "Sobremesas", 2, 32.00, 0.00, 6.0, "completed", "balcao"),

    # ORD-107: App
    ("ORD-107", "2026-11-07T20:45:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 10.00, 28.0, "completed", "app"),
    ("ORD-107", "2026-11-07T20:45:00Z", "Cannoli Siciliano Pistache", "Sobremesas", 2, 24.00, 0.00, 5.0, "completed", "app"),

    # ORD-108: Delivery
    ("ORD-108", "2026-11-07T21:00:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 0.00, 31.0, "completed", "delivery"),
    ("ORD-108", "2026-11-07T21:00:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 10.00, 35.0, "completed", "delivery"),

    # ORD-109: Balcão
    ("ORD-109", "2026-11-07T21:15:00Z", "Burrata com Pesto e Focaccia", "Entradas", 1, 58.00, 0.00, 14.0, "completed", "balcao"),
    ("ORD-109", "2026-11-07T21:15:00Z", "Vinho Chianti Reserva Taca", "Bebidas", 1, 34.00, 0.00, 3.0, "completed", "balcao"),

    # ORD-110: Delivery
    ("ORD-110", "2026-11-07T21:30:00Z", "Pizza Parma & Rucola", "Pizzas", 1, 94.00, 5.00, 33.0, "completed", "delivery"),

    # Sábado - 08/11/2026 (Dia de Alto Movimento)
    # ORD-111: Balcão Almoço/Happy Hour
    ("ORD-111", "2026-11-08T18:00:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 0.00, 20.0, "completed", "balcao"),
    ("ORD-111", "2026-11-08T18:00:00Z", "Cerveja Artesanal IPA 500ml", "Bebidas", 3, 26.00, 6.00, 3.0, "completed", "balcao"),

    # ORD-112: App
    ("ORD-112", "2026-11-08T18:25:00Z", "Pizza Calabresa Artesanal", "Pizzas", 2, 68.00, 15.00, 26.0, "completed", "app"),
    ("ORD-112", "2026-11-08T18:25:00Z", "Refrigerante 2L Guarana", "Bebidas", 1, 16.00, 0.00, 2.0, "completed", "app"),

    # ORD-113: Delivery
    ("ORD-113", "2026-11-08T18:45:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 0.00, 38.0, "completed", "delivery"),
    ("ORD-113", "2026-11-08T18:45:00Z", "Tiramisu Tradicional", "Sobremesas", 1, 32.00, 0.00, 5.0, "completed", "delivery"),

    # ORD-114: Balcão
    ("ORD-114", "2026-11-08T19:00:00Z", "Crostini Gorgonzola e Mel", "Entradas", 2, 42.00, 5.00, 15.0, "completed", "balcao"),
    ("ORD-114", "2026-11-08T19:00:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 0.00, 21.0, "completed", "balcao"),
    ("ORD-114", "2026-11-08T19:00:00Z", "Vinho Chianti Reserva Taca", "Bebidas", 2, 34.00, 0.00, 3.0, "completed", "balcao"),

    # ORD-115: Delivery
    ("ORD-115", "2026-11-08T19:20:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 10.00, 34.0, "completed", "delivery"),
    ("ORD-115", "2026-11-08T19:20:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 0.00, 29.0, "completed", "delivery"),

    # ORD-116: App - Cancelado
    ("ORD-116", "2026-11-08T19:35:00Z", "Pizza Parma & Rucola", "Pizzas", 1, 94.00, 0.00, 45.0, "canceled", "app"),
    ("ORD-116", "2026-11-08T19:35:00Z", "Cannoli Siciliano Pistache", "Sobremesas", 1, 24.00, 0.00, 5.0, "canceled", "app"),

    # ORD-117: Balcão
    ("ORD-117", "2026-11-08T19:50:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 0.00, 23.0, "completed", "balcao"),
    ("ORD-117", "2026-11-08T19:50:00Z", "Burrata com Pesto e Focaccia", "Entradas", 1, 58.00, 0.00, 13.0, "completed", "balcao"),

    # ORD-118: Delivery
    ("ORD-118", "2026-11-08T20:10:00Z", "Pizza Margherita Especial", "Pizzas", 3, 74.00, 20.00, 42.0, "completed", "delivery"),
    ("ORD-118", "2026-11-08T20:10:00Z", "Refrigerante 2L Guarana", "Bebidas", 2, 16.00, 0.00, 2.0, "completed", "delivery"),

    # ORD-119: App
    ("ORD-119", "2026-11-08T20:30:00Z", "Pizza Calabresa Artesanal", "Pizzas", 2, 68.00, 10.00, 27.0, "completed", "app"),
    ("ORD-119", "2026-11-08T20:30:00Z", "Cerveja Artesanal IPA 500ml", "Bebidas", 2, 26.00, 0.00, 3.0, "completed", "app"),

    # ORD-120: Delivery - Cancelado
    ("ORD-120", "2026-11-08T20:45:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 0.00, 52.0, "canceled", "delivery"),

    # ORD-121: Balcão
    ("ORD-121", "2026-11-08T21:05:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 0.00, 19.0, "completed", "balcao"),
    ("ORD-121", "2026-11-08T21:05:00Z", "Tiramisu Tradicional", "Sobremesas", 2, 32.00, 5.00, 4.0, "completed", "balcao"),

    # ORD-122: Delivery
    ("ORD-122", "2026-11-08T21:20:00Z", "Pizza Parma & Rucola", "Pizzas", 1, 94.00, 0.00, 37.0, "completed", "delivery"),
    ("ORD-122", "2026-11-08T21:20:00Z", "Crostini Gorgonzola e Mel", "Entradas", 1, 42.00, 0.00, 14.0, "completed", "delivery"),

    # Domingo - 09/11/2026 (Noite da Família)
    # ORD-123: Delivery
    ("ORD-123", "2026-11-09T18:15:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 10.00, 25.0, "completed", "delivery"),
    ("ORD-123", "2026-11-09T18:15:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 0.00, 24.0, "completed", "delivery"),

    # ORD-124: App
    ("ORD-124", "2026-11-09T18:40:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 5.00, 28.0, "completed", "app"),
    ("ORD-124", "2026-11-09T18:40:00Z", "Cannoli Siciliano Pistache", "Sobremesas", 2, 24.00, 0.00, 4.0, "completed", "app"),

    # ORD-125: Balcão
    ("ORD-125", "2026-11-09T19:00:00Z", "Burrata com Pesto e Focaccia", "Entradas", 2, 58.00, 10.00, 12.0, "completed", "balcao"),
    ("ORD-125", "2026-11-09T19:00:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 0.00, 22.0, "completed", "balcao"),
    ("ORD-125", "2026-11-09T19:00:00Z", "Vinho Chianti Reserva Taca", "Bebidas", 4, 34.00, 16.00, 3.0, "completed", "balcao"),

    # ORD-126: Delivery
    ("ORD-126", "2026-11-09T19:25:00Z", "Pizza Margherita Especial", "Pizzas", 2, 74.00, 10.00, 39.0, "completed", "delivery"),
    ("ORD-126", "2026-11-09T19:25:00Z", "Refrigerante 2L Guarana", "Bebidas", 1, 16.00, 0.00, 2.0, "completed", "delivery"),

    # ORD-127: Delivery
    ("ORD-127", "2026-11-09T19:45:00Z", "Pizza Parma & Rucola", "Pizzas", 2, 94.00, 10.00, 44.0, "completed", "delivery"),
    ("ORD-127", "2026-11-09T19:45:00Z", "Tiramisu Tradicional", "Sobremesas", 2, 32.00, 0.00, 5.0, "completed", "delivery"),

    # ORD-128: App
    ("ORD-128", "2026-11-09T20:00:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 0.00, 26.0, "completed", "app"),
    ("ORD-128", "2026-11-09T20:00:00Z", "Cerveja Artesanal IPA 500ml", "Bebidas", 1, 26.00, 0.00, 2.0, "completed", "app"),

    # ORD-129: Balcão
    ("ORD-129", "2026-11-09T20:20:00Z", "Pizza Quatro Queijos Trufada", "Pizzas", 1, 88.00, 0.00, 21.0, "completed", "balcao"),
    ("ORD-129", "2026-11-09T20:20:00Z", "Cannoli Siciliano Pistache", "Sobremesas", 1, 24.00, 0.00, 4.0, "completed", "balcao"),

    # ORD-130: Delivery
    ("ORD-130", "2026-11-09T20:40:00Z", "Pizza Margherita Especial", "Pizzas", 1, 74.00, 0.00, 32.0, "completed", "delivery"),
    ("ORD-130", "2026-11-09T20:40:00Z", "Crostini Gorgonzola e Mel", "Entradas", 1, 42.00, 0.00, 14.0, "completed", "delivery"),

    # ORD-131: Delivery - Cancelado
    ("ORD-131", "2026-11-09T21:00:00Z", "Pizza Parma & Rucola", "Pizzas", 1, 94.00, 0.00, 49.0, "canceled", "delivery"),

    # ORD-132: Balcão
    ("ORD-132", "2026-11-09T21:15:00Z", "Pizza Calabresa Artesanal", "Pizzas", 1, 68.00, 0.00, 18.0, "completed", "balcao"),
    ("ORD-132", "2026-11-09T21:15:00Z", "Cerveja Artesanal IPA 500ml", "Bebidas", 1, 26.00, 0.00, 2.0, "completed", "balcao"),
]

columns = [
    "order_id",
    "timestamp",
    "item_name",
    "category",
    "quantity",
    "unit_price",
    "discount",
    "prep_time_minutes",
    "status",
    "channel",
]

df = pd.DataFrame(orders_data, columns=columns)
output_path = Path("data/pizzeria_sample_orders.csv")
df.to_csv(output_path, index=False, float_format="%.2f")
print(f"Salvo {output_path} com {len(df)} linhas!")

# Teste de validação rigoroso com o pipeline oficial do FoodPilot AI
with open(output_path, "rb") as f:
    csv_bytes = f.read()

validated_df = validate_and_parse_csv(csv_bytes)
metrics = calculate_metrics(validated_df)

print("\n--- Validação do FoodPilot AI com o Novo Dataset ---")
print(f"Total de Linhas: {metrics['total_rows']}")
print(f"Pedidos Válidos: {metrics['valid_orders_count']}")
print(f"Pedidos Cancelados: {metrics['canceled_orders_count']}")
print(f"Receita Bruta: R$ {metrics['financials']['gross_revenue']:.2f}")
print(f"Descontos: R$ {metrics['financials']['discount_total']:.2f}")
print(f"Receita Líquida: R$ {metrics['financials']['net_revenue']:.2f}")
print(f"Perda por Cancelamento: R$ {metrics['financials']['canceled_revenue_loss']:.2f}")
print(f"Ticket Médio Líquido: R$ {metrics['financials']['average_ticket_net']:.2f}")
print(f"Top Produto Curva ABC: {metrics['summary_metrics']['top_abc_item']}")
print(f"Total de Anomalias Operacionais: {len(metrics['bottlenecks']['anomalies'])}")
for anom in metrics['bottlenecks']['anomalies']:
    print(f"  * [{anom['severity'].upper()}] {anom['dimension']}: {anom['description']} ({anom['metric_value']} vs limiar {anom['threshold_value']})")

