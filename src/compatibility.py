"""
Verificação de compatibilidade básica entre peças.

Regras implementadas:
  1. CPU AMD (AM4/AM5) deve ter placa-mãe com socket compatível.
  2. CPU Intel (LGA1700) deve ter placa-mãe com socket compatível.
  3. Placa-mãe DDR4 não combina com RAM DDR5 (e vice-versa).
  4. PSU deve ter potência estimada suficiente para CPU + GPU.
  5. Configuração deve ter todas as categorias obrigatórias.

Quando o dataset não possui os campos necessários, as regras são
aplicadas via heurística baseada no nome da peça.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CompatibilityReport:
    is_compatible: bool
    warnings: list[str]
    errors: list[str]
    summary: str


# Mapeamento soquete → marca CPU
AMD_SOCKETS = {"AM4", "AM5", "sTRX4", "sWRX8"}
INTEL_SOCKETS = {"LGA1700", "LGA1200", "LGA2066", "LGA4677"}

# Consumo estimado de GPUs por faixa (W)
GPU_TDP_ESTIMATES = {
    "rtx 4090": 450, "rtx 4080": 320, "rtx 4070 ti": 285,
    "rtx 4070": 200, "rtx 4060 ti": 165, "rtx 4060": 115,
    "rtx 3090": 350, "rtx 3080": 320, "rtx 3070": 220,
    "rtx 3060 ti": 200, "rtx 3060": 170,
    "rx 7900": 330, "rx 7800": 263, "rx 7700": 245,
    "rx 6900": 300, "rx 6800": 250, "rx 6700": 230,
    "rx 6600": 132, "gtx 1080": 180, "gtx 1070": 150,
}

# Consumo estimado de CPUs (W TDP)
CPU_TDP_ESTIMATES = {
    "i9": 125, "i7": 65, "i5": 65, "i3": 60,
    "ryzen 9": 170, "ryzen 7": 105, "ryzen 5": 65, "ryzen 3": 45,
}


def check_compatibility(selected_items: list[dict]) -> CompatibilityReport:
    """
    Verifica a compatibilidade básica de uma lista de peças selecionadas.

    Args:
        selected_items: lista de dicionários com campos 'name', 'category',
                        'socket', 'memory_type', 'wattage'.

    Returns:
        CompatibilityReport com avisos e erros encontrados.
    """
    warnings: list[str] = []
    errors: list[str] = []

    by_category: dict[str, list[dict]] = {}
    for item in selected_items:
        cat = item.get("category", "Desconhecido")
        by_category.setdefault(cat, []).append(item)

    _check_required_categories(by_category, errors)
    _check_cpu_motherboard(by_category, warnings, errors)
    _check_ram_motherboard(by_category, warnings)
    _check_psu_power(by_category, warnings)

    is_compatible = len(errors) == 0
    summary = (
        "Configuração compatível." if is_compatible
        else f"{len(errors)} problema(s) de compatibilidade encontrado(s)."
    )

    return CompatibilityReport(
        is_compatible=is_compatible,
        warnings=warnings,
        errors=errors,
        summary=summary,
    )


def _check_required_categories(
    by_category: dict[str, list[dict]],
    errors: list[str],
) -> None:
    required = ["CPU", "Motherboard", "RAM", "Storage", "PSU", "Case"]
    for cat in required:
        if cat not in by_category:
            errors.append(f"Categoria obrigatória ausente: {cat}")


def _check_cpu_motherboard(
    by_category: dict[str, list[dict]],
    warnings: list[str],
    errors: list[str],
) -> None:
    cpus = by_category.get("CPU", [])
    motherboards = by_category.get("Motherboard", [])
    if not cpus or not motherboards:
        return

    cpu = cpus[0]
    mb = motherboards[0]

    cpu_socket = str(cpu.get("socket", "")).strip()
    mb_socket = str(mb.get("socket", "")).strip()
    cpu_name_lower = cpu.get("name", "").lower()
    mb_name_lower = mb.get("name", "").lower()

    # Tenta via campo socket primeiro
    if cpu_socket and mb_socket:
        if cpu_socket != mb_socket:
            errors.append(
                f"Incompatibilidade de socket: CPU usa {cpu_socket}, "
                f"placa-mãe usa {mb_socket}."
            )
        return

    # Heurística pelo nome
    is_amd_cpu = "ryzen" in cpu_name_lower or "amd" in cpu_name_lower
    is_intel_cpu = "intel" in cpu_name_lower or "core i" in cpu_name_lower
    is_amd_mb = any(s in mb_name_lower for s in ["b450", "b550", "x570", "b650", "x670", "a520"])
    is_intel_mb = any(s in mb_name_lower for s in ["h610", "b660", "z690", "b760", "z790", "h670"])

    if is_amd_cpu and is_intel_mb:
        errors.append(
            f"Incompatibilidade: CPU AMD '{cpu['name']}' com "
            f"placa-mãe Intel '{mb['name']}'."
        )
    elif is_intel_cpu and is_amd_mb:
        errors.append(
            f"Incompatibilidade: CPU Intel '{cpu['name']}' com "
            f"placa-mãe AMD '{mb['name']}'."
        )


def _check_ram_motherboard(
    by_category: dict[str, list[dict]],
    warnings: list[str],
) -> None:
    rams = by_category.get("RAM", [])
    motherboards = by_category.get("Motherboard", [])
    if not rams or not motherboards:
        return

    ram = rams[0]
    mb = motherboards[0]

    mb_mem_type = str(mb.get("memory_type", "")).upper()
    ram_name_lower = ram.get("name", "").lower()

    if not mb_mem_type:
        return

    ram_is_ddr5 = "ddr5" in ram_name_lower
    mb_is_ddr5 = "DDR5" in mb_mem_type
    mb_is_ddr4 = "DDR4" in mb_mem_type

    if ram_is_ddr5 and mb_is_ddr4:
        warnings.append(
            f"Possível incompatibilidade: RAM DDR5 '{ram['name']}' "
            f"em placa-mãe DDR4 '{mb['name']}'."
        )
    elif not ram_is_ddr5 and mb_is_ddr5:
        warnings.append(
            f"Possível incompatibilidade: RAM DDR4 '{ram['name']}' "
            f"em placa-mãe DDR5 '{mb['name']}'."
        )


def _check_psu_power(
    by_category: dict[str, list[dict]],
    warnings: list[str],
) -> None:
    psus = by_category.get("PSU", [])
    cpus = by_category.get("CPU", [])
    gpus = by_category.get("GPU", [])

    if not psus:
        return

    psu = psus[0]
    psu_wattage = float(psu.get("wattage", 0))
    if psu_wattage == 0:
        # Tenta extrair do nome: "650W", "750W", etc.
        import re
        match = re.search(r"(\d{3,4})[Ww]", psu.get("name", ""))
        psu_wattage = float(match.group(1)) if match else 0

    if psu_wattage == 0:
        return

    estimated_consumption = 50  # sistema base (placa-mãe, RAM, SSD, etc.)

    for cpu in cpus:
        cpu_watt = float(cpu.get("wattage", 0))
        if cpu_watt == 0:
            cpu_name_lower = cpu.get("name", "").lower()
            for key, tdp in CPU_TDP_ESTIMATES.items():
                if key in cpu_name_lower:
                    cpu_watt = tdp
                    break
        estimated_consumption += cpu_watt or 65

    for gpu in gpus:
        gpu_watt = float(gpu.get("wattage", 0))
        if gpu_watt == 0:
            gpu_name_lower = gpu.get("name", "").lower()
            for key, tdp in GPU_TDP_ESTIMATES.items():
                if key in gpu_name_lower:
                    gpu_watt = tdp
                    break
        estimated_consumption += gpu_watt or 150

    # Recomenda 20% de folga
    recommended = estimated_consumption * 1.2
    if psu_wattage < recommended:
        warnings.append(
            f"Fonte de {psu_wattage:.0f}W pode ser insuficiente. "
            f"Consumo estimado: {estimated_consumption:.0f}W "
            f"(recomendado: {recommended:.0f}W com 20% de folga)."
        )


def get_compatibility_emoji(report: CompatibilityReport) -> str:
    if report.errors:
        return "❌"
    if report.warnings:
        return "⚠️"
    return "✅"
