# NBA Sports Betting Expert System Chatbot 🏀🤖

Un sistema experto completamente funcional para análisis de apuestas deportivas de la NBA que combina reglas expertas basadas en conocimiento con redes bayesianas para proporcionar recomendaciones de apuestas informadas.

## 🏀 Características Principales

### 1. **Obtención de Datos en Tiempo Real**
- **TheSportsDB API**: Obtiene juegos próximos de la NBA con caché inteligente (24 horas)
- **NBA API**: Estadísticas detalladas de equipos, jugadores, historial de juegos
- **Sistema de Caché**: Almacenamiento local con invalidación automática
- **Respeto a Límites de API**: Delays automáticos para evitar rate limiting

### 2. **Interacción de Usuario Intuitiva**
- Lista de juegos próximos reales obtenidos de TheSportsDB
- Selección de juegos programados o análisis manual de cualquier par de equipos
- Validación robusta de nombres de equipos con matching inteligente
- Manejo graceful de errores de entrada

### 3. **Motor de Conocimiento Experto**
- **Reglas Expertas**: Sistema basado en reglas IF-THEN usando Experta
- **Conocimiento Deportivo**: Reglas como "Si un equipo ha perdido 3+ juegos consecutivos y su mejor anotador está lesionado, la apuesta es de alto riesgo"
- **Análisis Estadístico**: Evaluación de racha actual, récord en casa/visitante, lesiones

### 4. **Análisis Probabilístico Avanzado**
- **Redes Bayesianas**: Usando pgmpy para manejar incertidumbre
- **Inferencia Probabilística**: Calcula probabilidades de riesgo basadas en múltiples factores
- **Combinación de Enfoques**: Fusiona razonamiento simbólico y probabilístico

### 5. **Arquitectura Modular y Escalable**
- **Diseño Limpio**: Separación clara de responsabilidades
- **Código Mantenible**: Bien comentado y estructurado
- **Extensible**: Fácil agregar nuevas reglas o fuentes de datos
- **Logging Completo**: Trazabilidad de decisiones del sistema

## 🚀 Instalación y Configuración

### Requisitos Previos
- **Python 3.9** (recomendado para compatibilidad completa)
- pip (gestor de paquetes de Python)

### Instalación Paso a Paso

1. **Clonar o descargar el proyecto**
```bash
cd tu-directorio-del-proyecto
```

2. **Instalar Python 3.9 (si no lo tienes)**
```bash
# En macOS con Homebrew
brew install python@3.9

# Verificar instalación
python3.9 --version
```

3. **Crear entorno virtual con Python 3.9**
```bash
python3.9 -m venv venv
```

4. **Activar el entorno virtual**
```bash
# En macOS/Linux
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

5. **Actualizar pip**
```bash
pip install --upgrade pip
```

6. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### Verificación de Instalación
```bash
python -c "import experta, pgmpy, nba_api; print('✅ Todas las dependencias instaladas correctamente')"
```

## 🎮 Uso del Sistema

### Ejecutar el Chatbot
```bash
python nba_chatbot.py
```

### Opciones de Análisis

1. **Seleccionar de Juegos Próximos**
   - El sistema muestra juegos reales obtenidos de TheSportsDB
   - Selecciona un número de la lista para análisis automático

2. **Análisis Manual de Equipos**
   - Ingresa nombres de dos equipos manualmente
   - El sistema busca y analiza cualquier par de equipos NBA
   - Funciona incluso si no tienen juego programado

### Ejemplos de Entrada Válida
```
- "1" (seleccionar primer juego de la lista)
- "Lakers vs Warriors"
- "Boston Celtics, Miami Heat"
- "lakers warriors" (matching flexible)
```

## 🧠 Cómo Funciona

### 1. Motor de Reglas Expertas (Experta)
```python
# Ejemplo de regla implementada
@Rule(Fact(consecutive_losses__gt=2), 
      Fact(key_players_injured=True))
def high_risk_injured_losing_streak(self):
    self.declare(Fact(risk_level="HIGH"))
    self.add_explanation("Alto riesgo: Racha perdedora + lesiones clave")
```

### 2. Red Bayesiana (pgmpy)
- **Variables**: Racha, lesiones, récord casa/visitante, rendimiento reciente
- **Inferencia**: Calcula probabilidades de riesgo considerando incertidumbre
- **Combinación**: Fusiona con reglas expertas para decisión final

### 3. Fuentes de Datos
- **TheSportsDB**: Juegos próximos, información básica de equipos
- **NBA API**: Estadísticas detalladas, logs de juegos, rendimiento

## 📁 Estructura del Proyecto

```
nba_chatbot/
├── nba_chatbot.py          # Aplicación principal del chatbot
├── data_fetcher.py         # Obtención y caché de datos de APIs
├── expert_engine.py        # Motor de reglas expertas con Experta
├── bayesian_analyzer.py    # Análisis probabilístico con pgmpy
├── models.py              # Modelos de datos (GameInfo, TeamStats)
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Documentación del proyecto
└── cache/                # Directorio de caché automático
    ├── upcoming_games.json
    └── team_stats_*.json
```

## 🔍 Ejemplo de Análisis Completo

```
=== ANÁLISIS DE APUESTA: Lakers vs Warriors ===

📊 ESTADÍSTICAS:
Los Angeles Lakers: 15-12 (55.6%) | Racha: L3 | Casa: 8-5 | Lesiones: Anthony Davis
Golden State Warriors: 18-9 (66.7%) | Racha: W2 | Visitante: 7-6 | Lesiones: Ninguna

🧠 REGLAS ACTIVADAS:
✓ Alto riesgo: Racha perdedora de 3+ juegos (Lakers)
✓ Lesión de jugador clave detectada (Lakers)
✓ Diferencia significativa en porcentaje de victorias

📈 ANÁLISIS BAYESIANO:
- Probabilidad de riesgo alto: 78%
- Factores principales: Lesiones (40%), Racha actual (35%), Récord (25%)

🎯 RECOMENDACIÓN FINAL: APUESTA DE ALTO RIESGO
Razón: Lakers en mala racha con lesión clave vs Warriors en forma
```

## ⚡ Características Avanzadas

### Sistema de Caché Inteligente
- **Juegos próximos**: Cache de 24 horas (respeta límites de API)
- **Estadísticas de equipos**: Cache de 6 horas (datos frescos)
- **Invalidación automática**: Se actualiza cuando expira

### Matching Inteligente de Equipos
```python
# Acepta múltiples formatos
"Lakers" → "Los Angeles Lakers"
"Warriors" → "Golden State Warriors"  
"76ers" → "Philadelphia 76ers"
"Cavs" → "Cleveland Cavaliers"
```

### Manejo Robusto de Errores
- Fallback a datos en caché si la API falla
- Validación de entrada de usuario
- Mensajes de error informativos
- Recuperación graceful de errores de red

## 🛠️ Tecnologías Utilizadas

- **Python 3.9**: Lenguaje principal
- **Experta**: Motor de sistema experto para reglas IF-THEN
- **pgmpy**: Redes bayesianas y inferencia probabilística
- **nba_api**: API oficial de estadísticas NBA
- **requests**: Cliente HTTP para TheSportsDB API
- **pandas**: Manipulación y análisis de datos
- **numpy**: Computación numérica
- **networkx**: Análisis de grafos para redes bayesianas
- **scikit-learn**: Herramientas de machine learning

## 📝 Dependencias (requirements.txt)

```
requests==2.32.3
nba-api==1.5.2
experta==1.9.4
pgmpy==0.1.25
pandas==2.2.3
numpy==1.26.4
networkx==3.4.2
scikit-learn==1.5.2
```

### Notas sobre Compatibilidad
- **Python 3.9**: Versión recomendada para compatibilidad completa
- **pgmpy==0.1.25**: Versión específica compatible con Python 3.9
- **Experta**: Requiere frozendict==1.2 (se instala automáticamente)

## 🔧 Solución de Problemas

### Error de Compatibilidad con Python 3.12
Si usas Python 3.12, puedes encontrar errores con frozendict. Solución:
1. Usar Python 3.9 (recomendado)
2. O instalar versiones específicas compatibles

### Error de NBA API Rate Limiting
El sistema incluye delays automáticos, pero si encuentras errores:
- Espera unos minutos entre consultas
- Los datos se guardan en caché para evitar llamadas repetidas

### Problemas con Cache
Si encuentras datos obsoletos:
```bash
rm -rf cache/  # Eliminar caché
python nba_chatbot.py  # Ejecutar de nuevo
```

## 📚 Notas de Desarrollo

### Decisiones de Diseño
1. **Python 3.9**: Elegido por compatibilidad completa con todas las librerías
2. **Caché local**: Mejora rendimiento y respeta límites de API
3. **Arquitectura modular**: Facilita mantenimiento y extensión
4. **Doble enfoque**: Combina reglas expertas con análisis probabilístico

### Posibles Mejoras Futuras
- Integración con APIs de lesiones en tiempo real
- Machine learning para predicciones más sofisticadas
- Interfaz web con Flask/Django
- Base de datos para histórico de predicciones
- API REST para integración con otras aplicaciones

## 👥 Contributors

- [Davide Flamini](https://github.com/davidone007)
- [Andrés Cabezas](https://github.com/andrescabezas26)
- [Nicolas Cuellar](https://github.com/Nicolas-CM)

## 📄 Licencia

Proyecto desarrollado con fines educativos. Uso libre para aprendizaje y desarrollo.

---

**Sistema Experto NBA - Combinando IA simbólica y probabilística para análisis deportivo inteligente** 🏀🤖
