# 🏛️ Gemelo Digital Financiero (Financial Digital Twin - FDT)
## Mercado de Tarjetas de Crédito en Colombia (2021–2026)

Este repositorio contiene la arquitectura completa, modelos econométricos, algoritmos de clustering comportamental y la aplicación interactiva en Streamlit para el **Gemelo Digital Financiero (FDT)** del mercado de tarjetas de crédito en Colombia.

---

## 📌 Descripción del Proyecto

El **Gemelo Digital Financiero (FDT)** es un entorno virtual de simulación analítica y prospectiva desarrollado bajo la metodología de **Piedad Cristina Martínez Carazo (2006)** e integrado con datos abiertos oficiales de la **Superintendencia Financiera de Colombia (SFC)** (Dataset `h2jg-r3zg`). 

Diseñado como un **Laboratorio de Toma de Decisiones y Gobernanza de IA**, el FDT permite simular en tiempo real la dinámica de las plataformas de múltiples lados (*Multi-Sided Platforms*), las respuestas de demanda ante shocks de tasas de interés y los patrones de segmentación del consumidor.

---

## 📑 Estructura del Dashboard Interactivo

La aplicación web (`app_dashboard.py`) está integrada por 4 capas analíticas interactivas desarrolladas en **Streamlit** y **Plotly**:

1. **📈 Capa 1: Serie Temporal e Ingesta SFC:** Visualización y comparación del volumen histórico de plásticos e indicadores del mercado entre 2021 y 2026, permitiendo identificar inercia y volatilidad por entidad bancaria.
2. **🕸️ Capa 2: Constelación Financiera (Red Multilado):** Modela la economía de red entre emisores, adquirentes, redes (*switches*), franquicias, comercios y tarjetahabientes, desglosando la composición del margen operativo neto ($I_{int}$, $I_{mdr}$ y cuotas de manejo).
3. **🎯 Capa 3: Segmentación Comportamental (K-Means / RFM):** Agrupa la demanda en 4 perfiles tipológicos (*Inercial/Masivo, Transaccional Frecuente, Financiado de Alta Volatilidad y Líder de Red/Escala*), capturando las brechas entre la oferta bancaria y el sistema afectivo-cognoscitivo del usuario.
4. **⚖️ Capa 4: Modelo Econométrico de Diferenciación (Logit Multinomial):** Simula la respuesta de la cuota de mercado ante variaciones de precio y shocks en la Tasa de Usura, calculando la **Inelasticidad Cruzada** ($\eta_{ij}$) y el valor de la diferenciación intangible.

---

## 🚀 Estructura del Repositorio

```text
├── data/                                 # Microdatos procesados de la SFC (h2jg-r3zg)
├── outputs/                              # Resultados de simulaciones, K-Means y econometría
├── app_dashboard.py                      # Aplicación principal de Streamlit (Dashboard)
├── ingesta_gemelo.py                     # Extracción y limpieza de datos abiertos
├── analisis_descriptivo_gemelo.py        # Series temporales e indicadores del sector
├── simulacion_constelacion.py            # Modelado económico de la red multilado
├── perfilamiento_clientes.py             # Clustering K-Means y análisis RFM
├── modelo_econometrico_diferenciacion.py # Estimación econométrica Logit e Inelasticidad
├── requirements.txt                      # Dependencias del proyecto para despliegue en la nube
└── README.md                             # Documentación general del repositorio
