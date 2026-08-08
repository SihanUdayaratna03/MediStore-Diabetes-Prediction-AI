"""
Clinical Data MCP Server
=========================
Provides tools for interpreting patient clinical data:
- `interpret_patient_data`: Takes patient vitals and returns clinical interpretation
- `get_risk_thresholds`: Returns clinical thresholds for a given biomarker
"""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

app = Server("clinical-data-mcp-server")

# Clinical thresholds reference (ADA 2024 Guidelines)
CLINICAL_THRESHOLDS = {
    "glucose": {
        "normal": {"min": 70, "max": 99},
        "prediabetes": {"min": 100, "max": 125},
        "diabetes": {"min": 126, "max": 999},
        "unit": "mg/dL",
        "fasting": True,
    },
    "bmi": {
        "underweight": {"min": 0, "max": 18.4},
        "normal": {"min": 18.5, "max": 24.9},
        "overweight": {"min": 25.0, "max": 29.9},
        "obese": {"min": 30.0, "max": 999},
        "unit": "kg/m²",
    },
    "blood_pressure": {
        "normal": {"min": 0, "max": 79},
        "elevated": {"min": 80, "max": 89},
        "high": {"min": 90, "max": 999},
        "unit": "mm Hg (diastolic)",
    },
    "hba1c": {
        "normal": {"min": 0, "max": 5.6},
        "prediabetes": {"min": 5.7, "max": 6.4},
        "diabetes": {"min": 6.5, "max": 999},
        "unit": "%",
    },
}

TOOLS = [
    types.Tool(
        name="interpret_patient_data",
        description=(
            "Interprets a patient's clinical measurements against ADA 2024 thresholds "
            "and returns a structured clinical summary."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "glucose":         {"type": "number", "description": "Fasting plasma glucose in mg/dL"},
                "bmi":             {"type": "number", "description": "Body Mass Index"},
                "blood_pressure":  {"type": "number", "description": "Diastolic BP in mm Hg"},
                "age":             {"type": "integer", "description": "Patient age in years"},
                "dpf":             {"type": "number", "description": "Diabetes Pedigree Function"},
                "prediction":      {"type": "integer", "description": "Model prediction: 0=no diabetes, 1=diabetes"},
                "probability":     {"type": "number", "description": "Probability of diabetes (0.0 to 1.0)"},
            },
            "required": ["glucose", "bmi", "prediction"],
        },
    ),
    types.Tool(
        name="get_risk_thresholds",
        description="Returns clinical threshold ranges for a specific biomarker.",
        inputSchema={
            "type": "object",
            "properties": {
                "biomarker": {
                    "type": "string",
                    "enum": ["glucose", "bmi", "blood_pressure", "hba1c"],
                    "description": "The biomarker to get thresholds for.",
                }
            },
            "required": ["biomarker"],
        },
    ),
]


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return TOOLS


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:

    if name == "interpret_patient_data":
        glucose    = arguments.get("glucose", 0)
        bmi        = arguments.get("bmi", 0)
        bp         = arguments.get("blood_pressure", 70)
        age        = arguments.get("age", 0)
        dpf        = arguments.get("dpf", 0)
        prediction = arguments.get("prediction", 0)
        prob       = arguments.get("probability", 0.5)

        # Classify glucose
        if glucose < 100:
            glucose_status = "Normal"
        elif glucose <= 125:
            glucose_status = "Prediabetes Range"
        else:
            glucose_status = "Diabetes Range ⚠️"

        # Classify BMI
        if bmi < 18.5:
            bmi_status = "Underweight"
        elif bmi <= 24.9:
            bmi_status = "Normal"
        elif bmi <= 29.9:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese ⚠️"

        # Age risk
        age_risk = "High age-related risk ⚠️" if age > 45 else "Low age-related risk"

        # Overall assessment
        risk_level = "HIGH" if prediction == 1 else "LOW"
        summary = f"""
Clinical Interpretation Summary
================================
• Prediction: {risk_level} RISK ({prob * 100:.1f}% probability)
• Glucose ({glucose} mg/dL): {glucose_status}
• BMI ({bmi:.1f}): {bmi_status}
• Blood Pressure (diastolic {bp} mm Hg): {"Elevated" if bp >= 80 else "Normal"}
• Age ({age} yrs): {age_risk}
• Diabetes Pedigree Function ({dpf:.2f}): {"High genetic predisposition" if dpf > 0.5 else "Low genetic predisposition"}

Recommended Actions:
{_get_recommendations(prediction, glucose, bmi, age)}
"""
        return [types.TextContent(type="text", text=summary)]

    elif name == "get_risk_thresholds":
        biomarker = arguments.get("biomarker", "")
        data      = CLINICAL_THRESHOLDS.get(biomarker)
        if not data:
            return [types.TextContent(type="text", text=f"Unknown biomarker: {biomarker}")]
        lines = [f"Clinical Thresholds for {biomarker.title()} ({data.get('unit', '')}):\n"]
        for key, val in data.items():
            if isinstance(val, dict) and "min" in val:
                lines.append(f"  • {key.title()}: {val['min']}–{val['max']}")
        return [types.TextContent(type="text", text="\n".join(lines))]

    raise ValueError(f"Unknown tool: {name}")


def _get_recommendations(prediction: int, glucose: float, bmi: float, age: int) -> str:
    if prediction == 1:
        return (
            "1. Consult an endocrinologist urgently\n"
            "2. Request full diabetes panel: HbA1c, fasting glucose, OGTT\n"
            "3. Begin blood glucose self-monitoring\n"
            "4. Dietary consultation and structured exercise programme"
        )
    elif glucose >= 100 or bmi >= 25:
        return (
            "1. Schedule annual HbA1c and fasting glucose screening\n"
            "2. Adopt Mediterranean or low-GI diet\n"
            "3. 150 min/week moderate aerobic exercise\n"
            "4. Aim for 5–7% weight reduction if overweight"
        )
    else:
        return (
            "1. Continue annual health screening\n"
            "2. Maintain healthy lifestyle\n"
            "3. Monitor weight, diet, and activity levels"
        )


async def main():
    print("🟢 Clinical Data MCP Server starting...", file=sys.stderr, flush=True)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
