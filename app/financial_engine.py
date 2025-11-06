"""
Moduł obliczeniowy dla kalkulatora opłacalności deweloperskiej.
Implementuje metodologie NPV (Net Present Value) i IRR (Internal Rate of Return).
"""

import numpy as np
import numpy_financial as npf
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class ProjectInputs:
    """Dane wejściowe projektu"""
    # Działka
    plot_area: float  # m²
    plot_price_per_sqm: float  # PLN/m²

    # Budynek
    pum_area: float  # m² powierzchni użytkowej mieszkań
    units_count: int
    sale_price_per_sqm: float  # PLN/m²
    parking_revenue: float  # PLN

    # Harmonogram (miesiące)
    preparation_months: int
    construction_months: int
    sales_months: int

    # Finansowe
    discount_rate: float  # % roczna
    expected_margin: float  # %
    tax_rate: float  # %

    # Kredyt
    loan_percentage: float  # %
    loan_interest_rate: float  # % roczna
    loan_provision: float  # %
    loan_months: int

    # Koszty jednostkowe (PLN/m² PUM lub stałe)
    acquisition_costs_pct: float  # % od wartości zakupu
    construction_cost_per_sqm: float  # PLN/m²
    design_cost_per_sqm: float  # PLN/m²
    infrastructure_cost_per_sqm: float  # PLN/m²
    overhead_cost_per_sqm: float  # PLN/m²
    reserve_cost_per_sqm: float  # PLN/m²
    marketing_cost_per_sqm: float  # PLN/m²
    sales_commission_pct: float  # % od przychodu


@dataclass
class CashFlowItem:
    """Element przepływu pieniężnego"""
    month: int
    phase: str  # preparation, construction, sales
    revenues: float
    costs: float
    net_cash_flow: float
    cumulative_cash_flow: float


@dataclass
class ProjectResults:
    """Wyniki obliczeń projektu"""
    # Podsumowanie finansowe
    total_revenue: float
    total_costs: float
    gross_margin: float
    margin_percentage: float

    # Wskaźniki opłacalności
    npv: float
    irr: float
    required_price_per_sqm: float

    # Rozkład kosztów
    cost_breakdown: Dict[str, float]

    # Szczegóły kredytu
    loan_details: Optional[Dict[str, float]]

    # Cash Flow
    cash_flow: List[CashFlowItem]
    monthly_cash_flows: List[float]

    # Analiza
    is_profitable: bool
    profitability_message: str


class FinancialEngine:
    """Silnik obliczeń finansowych"""

    def __init__(self, inputs: ProjectInputs):
        self.inputs = inputs

    def calculate_total_costs(self) -> Tuple[float, Dict[str, float]]:
        """Oblicza całkowite koszty projektu z rozbiciem"""
        pum = self.inputs.pum_area
        plot_value = self.inputs.plot_area * self.inputs.plot_price_per_sqm

        # 1. Zakup działki
        plot_cost = plot_value

        # 2. Koszty pozyskania
        acquisition_costs = plot_value * (self.inputs.acquisition_costs_pct / 100)

        # 3. Koszty projektowe
        design_costs = pum * self.inputs.design_cost_per_sqm

        # 4. Koszty infrastruktury
        infrastructure_costs = pum * self.inputs.infrastructure_cost_per_sqm

        # 5. Koszty budowy
        construction_costs = pum * self.inputs.construction_cost_per_sqm

        # 6. Overhead
        overhead_costs = pum * self.inputs.overhead_cost_per_sqm

        # 7. Rezerwa
        reserve_costs = pum * self.inputs.reserve_cost_per_sqm

        # 8. Marketing
        marketing_costs = pum * self.inputs.marketing_cost_per_sqm

        # 9. Prowizje sprzedażowe
        gross_revenue = self.inputs.pum_area * self.inputs.sale_price_per_sqm + self.inputs.parking_revenue
        sales_commission = gross_revenue * (self.inputs.sales_commission_pct / 100)

        # 10. Koszty kredytu (jeśli jest)
        loan_costs = 0
        if self.inputs.loan_percentage > 0:
            loan_costs = self.calculate_loan_costs()

        breakdown = {
            'plot_purchase': plot_cost,
            'acquisition': acquisition_costs,
            'design': design_costs,
            'infrastructure': infrastructure_costs,
            'construction': construction_costs,
            'overhead': overhead_costs,
            'reserve': reserve_costs,
            'marketing': marketing_costs,
            'sales_commission': sales_commission,
            'loan_costs': loan_costs
        }

        total_costs = sum(breakdown.values())
        return total_costs, breakdown

    def calculate_loan_costs(self) -> float:
        """Oblicza całkowite koszty kredytu (odsetki + prowizja)"""
        if self.inputs.loan_percentage == 0:
            return 0

        # Kwota kredytu
        total_investment = self.calculate_total_costs()[0]  # To może być rekurencyjne, ale upraszczamy
        # Lepiej: używamy szacunkowego kosztu bez kredytu
        estimated_costs = (
            self.inputs.plot_area * self.inputs.plot_price_per_sqm +
            self.inputs.pum_area * (
                self.inputs.construction_cost_per_sqm +
                self.inputs.design_cost_per_sqm +
                self.inputs.infrastructure_cost_per_sqm +
                self.inputs.overhead_cost_per_sqm +
                self.inputs.reserve_cost_per_sqm +
                self.inputs.marketing_cost_per_sqm
            )
        )

        loan_amount = estimated_costs * (self.inputs.loan_percentage / 100)

        # Prowizja
        provision = loan_amount * (self.inputs.loan_provision / 100)

        # Miesięczna stopa oprocentowania
        monthly_rate = (self.inputs.loan_interest_rate / 100) / 12

        # Miesięczna rata (annuity)
        if monthly_rate > 0:
            monthly_payment = npf.pmt(monthly_rate, self.inputs.loan_months, -loan_amount)
        else:
            monthly_payment = loan_amount / self.inputs.loan_months

        # Całkowity koszt (suma rat - kapitał)
        total_payments = monthly_payment * self.inputs.loan_months
        interest_costs = total_payments - loan_amount

        return interest_costs + provision

    def get_loan_details(self) -> Optional[Dict[str, float]]:
        """Zwraca szczegółowe informacje o kredycie"""
        if self.inputs.loan_percentage == 0:
            return None

        estimated_costs = (
            self.inputs.plot_area * self.inputs.plot_price_per_sqm +
            self.inputs.pum_area * (
                self.inputs.construction_cost_per_sqm +
                self.inputs.design_cost_per_sqm +
                self.inputs.infrastructure_cost_per_sqm +
                self.inputs.overhead_cost_per_sqm +
                self.inputs.reserve_cost_per_sqm +
                self.inputs.marketing_cost_per_sqm
            )
        )

        loan_amount = estimated_costs * (self.inputs.loan_percentage / 100)
        provision = loan_amount * (self.inputs.loan_provision / 100)
        monthly_rate = (self.inputs.loan_interest_rate / 100) / 12

        if monthly_rate > 0:
            monthly_payment = npf.pmt(monthly_rate, self.inputs.loan_months, -loan_amount)
        else:
            monthly_payment = loan_amount / self.inputs.loan_months

        total_payments = monthly_payment * self.inputs.loan_months
        interest_costs = total_payments - loan_amount

        return {
            'loan_amount': loan_amount,
            'provision': provision,
            'monthly_payment': monthly_payment,
            'total_payments': total_payments,
            'interest_costs': interest_costs,
            'total_loan_costs': interest_costs + provision
        }

    def generate_cash_flow(self) -> List[CashFlowItem]:
        """
        Generuje miesięczny harmonogram przepływów pieniężnych.

        Fazy:
        1. Przygotowanie (preparation_months): koszty działki, pozyskania, projektów
        2. Budowa (construction_months): koszty budowy, infrastruktury, overhead
        3. Sprzedaż (sales_months): przychody, prowizje

        Uwaga: Sprzedaż może zacząć się przed końcem budowy (nakładanie faz)
        """
        cash_flows = []
        cumulative = 0

        total_costs, breakdown = self.calculate_total_costs()
        total_revenue = self.inputs.pum_area * self.inputs.sale_price_per_sqm + self.inputs.parking_revenue

        total_months = self.inputs.preparation_months + self.inputs.construction_months + self.inputs.sales_months

        # Rozkład kosztów w czasie
        # Faza przygotowania (miesiące 0 do preparation_months)
        prep_costs_per_month = (
            breakdown['plot_purchase'] +
            breakdown['acquisition'] +
            breakdown['design']
        ) / self.inputs.preparation_months if self.inputs.preparation_months > 0 else 0

        # Faza budowy
        construction_costs_per_month = (
            breakdown['construction'] +
            breakdown['infrastructure'] +
            breakdown['overhead'] +
            breakdown['reserve']
        ) / self.inputs.construction_months if self.inputs.construction_months > 0 else 0

        # Faza sprzedaży - przychody rozłożone równomiernie
        # Zakładamy, że sprzedaż zaczyna się w trakcie budowy (np. 60% budowy = start sprzedaży)
        sales_start_month = self.inputs.preparation_months + int(self.inputs.construction_months * 0.6)
        revenue_per_month = total_revenue / self.inputs.sales_months if self.inputs.sales_months > 0 else 0

        # Marketing - przez całą fazę sprzedaży
        marketing_per_month = breakdown['marketing'] / self.inputs.sales_months if self.inputs.sales_months > 0 else 0

        # Prowizje - proporcjonalnie do przychodów
        commission_per_month = breakdown['sales_commission'] / self.inputs.sales_months if self.inputs.sales_months > 0 else 0

        for month in range(total_months):
            revenues = 0
            costs = 0
            phase = ''

            # Faza przygotowania
            if month < self.inputs.preparation_months:
                phase = 'preparation'
                costs += prep_costs_per_month

            # Faza budowy
            elif month < self.inputs.preparation_months + self.inputs.construction_months:
                phase = 'construction'
                costs += construction_costs_per_month

                # Jeśli sprzedaż już się zaczęła
                if month >= sales_start_month:
                    revenues += revenue_per_month
                    costs += marketing_per_month + commission_per_month

            # Faza sprzedaży (po budowie)
            else:
                phase = 'sales'
                revenues += revenue_per_month
                costs += marketing_per_month + commission_per_month

            net_cf = revenues - costs
            cumulative += net_cf

            cash_flows.append(CashFlowItem(
                month=month,
                phase=phase,
                revenues=revenues,
                costs=costs,
                net_cash_flow=net_cf,
                cumulative_cash_flow=cumulative
            ))

        return cash_flows

    def calculate_npv(self, cash_flows: List[CashFlowItem]) -> float:
        """
        Oblicza Net Present Value (NPV).

        NPV = Σ [CFt / (1 + r)^t]
        gdzie:
        - CFt = przepływ pieniężny w okresie t
        - r = stopa dyskontowa (miesięczna)
        - t = okres
        """
        monthly_discount_rate = (self.inputs.discount_rate / 100) / 12
        net_flows = [cf.net_cash_flow for cf in cash_flows]

        npv = npf.npv(monthly_discount_rate, net_flows)
        return npv

    def calculate_irr(self, cash_flows: List[CashFlowItem]) -> float:
        """
        Oblicza Internal Rate of Return (IRR).

        IRR to stopa dyskontowa, przy której NPV = 0.
        Zwraca wartość roczną (%).
        """
        net_flows = [cf.net_cash_flow for cf in cash_flows]

        try:
            # IRR miesięczny
            monthly_irr = npf.irr(net_flows)

            # Konwersja na roczny IRR
            annual_irr = ((1 + monthly_irr) ** 12 - 1) * 100

            # Sprawdzenie czy wynik jest sensowny
            if np.isnan(annual_irr) or np.isinf(annual_irr):
                return 0.0

            return annual_irr
        except:
            return 0.0

    def calculate_required_price(self, target_margin: float) -> float:
        """
        Oblicza wymaganą cenę sprzedaży PLN/m² PUM dla osiągnięcia docelowej marży.

        Marża = (Przychody - Koszty) / Koszty * 100%
        Przychody = Koszty * (1 + Marża/100)
        Cena/m² = (Przychody - parking_revenue) / PUM
        """
        total_costs, _ = self.calculate_total_costs()

        # Wymagane przychody
        required_revenue = total_costs * (1 + target_margin / 100)

        # Przychody z PUM (minus parkingi)
        required_pum_revenue = required_revenue - self.inputs.parking_revenue

        # Cena za m²
        required_price = required_pum_revenue / self.inputs.pum_area

        return required_price

    def analyze_profitability(self, npv: float, irr: float) -> Tuple[bool, str]:
        """Analizuje opłacalność projektu"""
        messages = []

        # Sprawdzenie NPV
        if npv >= 0:
            messages.append(f"✓ NPV dodatnie ({npv:,.2f} PLN) - projekt opłacalny")
        else:
            messages.append(f"✗ NPV ujemne ({npv:,.2f} PLN) - projekt nieopłacalny")

        # Sprawdzenie IRR
        min_irr = 15.0  # Minimalna oczekiwana stopa zwrotu
        if irr >= min_irr:
            messages.append(f"✓ IRR ({irr:.2f}%) powyżej minimum ({min_irr}%)")
        else:
            messages.append(f"✗ IRR ({irr:.2f}%) poniżej minimum ({min_irr}%)")

        is_profitable = npv >= 0 and irr >= min_irr
        return is_profitable, " | ".join(messages)

    def run_calculation(self) -> ProjectResults:
        """Wykonuje pełną kalkulację projektu"""

        # 1. Oblicz koszty
        total_costs, cost_breakdown = self.calculate_total_costs()

        # 2. Oblicz przychody
        total_revenue = (
            self.inputs.pum_area * self.inputs.sale_price_per_sqm +
            self.inputs.parking_revenue
        )

        # 3. Marża brutto
        gross_margin = total_revenue - total_costs
        margin_pct = (gross_margin / total_costs * 100) if total_costs > 0 else 0

        # 4. Generuj Cash Flow
        cash_flows = self.generate_cash_flow()

        # 5. Oblicz NPV i IRR
        npv = self.calculate_npv(cash_flows)
        irr = self.calculate_irr(cash_flows)

        # 6. Wymagana cena sprzedaży
        required_price = self.calculate_required_price(self.inputs.expected_margin)

        # 7. Szczegóły kredytu
        loan_details = self.get_loan_details()

        # 8. Analiza opłacalności
        is_profitable, profitability_msg = self.analyze_profitability(npv, irr)

        # 9. Lista miesięcznych przepływów netto (do wykresu)
        monthly_flows = [cf.net_cash_flow for cf in cash_flows]

        return ProjectResults(
            total_revenue=total_revenue,
            total_costs=total_costs,
            gross_margin=gross_margin,
            margin_percentage=margin_pct,
            npv=npv,
            irr=irr,
            required_price_per_sqm=required_price,
            cost_breakdown=cost_breakdown,
            loan_details=loan_details,
            cash_flow=cash_flows,
            monthly_cash_flows=monthly_flows,
            is_profitable=is_profitable,
            profitability_message=profitability_msg
        )


def run_sensitivity_analysis(
    base_inputs: ProjectInputs,
    variable_name: str,
    range_pct: float = 20,
    steps: int = 10
) -> List[Dict]:
    """
    Przeprowadza analizę wrażliwości dla wybranej zmiennej.

    Args:
        base_inputs: Bazowe dane wejściowe
        variable_name: Nazwa zmiennej do analizy (np. 'plot_price_per_sqm')
        range_pct: Zakres zmian w % (np. 20 = od -20% do +20%)
        steps: Liczba kroków analizy

    Returns:
        Lista słowników z wynikami dla każdego kroku
    """
    results = []

    base_value = getattr(base_inputs, variable_name)
    min_value = base_value * (1 - range_pct / 100)
    max_value = base_value * (1 + range_pct / 100)

    for value in np.linspace(min_value, max_value, steps):
        # Kopiuj inputs i zmień wartość
        inputs_dict = asdict(base_inputs)
        inputs_dict[variable_name] = value
        test_inputs = ProjectInputs(**inputs_dict)

        # Uruchom kalkulację
        engine = FinancialEngine(test_inputs)
        result = engine.run_calculation()

        results.append({
            'variable_value': value,
            'npv': result.npv,
            'irr': result.irr,
            'margin': result.margin_percentage
        })

    return results
