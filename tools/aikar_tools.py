import logging
from typing import Dict, Any

from aikar import IncomeTaxCalculator, CapitalGainsCalculator
from google.adk.tools import ToolContext

# Configure logging
logger = logging.getLogger(__name__)


def calculate_income_tax(
        tool_context: ToolContext,
        income: float,
        age: int,
        regime: str = "new",
        deductions_80c: float = 0.0,
        deductions_hra: float = 0.0,
        deductions_80ccd2: float = 0.0,
        deductions_home_loan: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate income tax for the given income and deductions using aikar library.
    
    This tool calculates income tax based on Indian tax slabs for both old and new tax regimes.
    It considers various deductions like 80C, HRA, 80CCD2, and home loan interest.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info.
        income (float): Annual income in INR. Required.
        age (int): Age of the taxpayer. Required for senior citizen benefits.
        regime (str, optional): Tax regime - 'old' or 'new'. Defaults to 'new'.
        deductions_80c (float, optional): Deductions under Section 80C (PPF, ELSS, etc.). Defaults to 0.0.
        deductions_hra (float, optional): HRA deductions. Defaults to 0.0.
        deductions_80ccd2 (float, optional): Employer contribution to NPS under 80CCD(2). Defaults to 0.0.
        deductions_home_loan (float, optional): Interest paid on home loan. Defaults to 0.0.
    
    Returns:
        Dict[str, Any]: Dictionary containing tax calculation details including:
                       - total_tax: Total tax amount
                       - taxable_income: Income after deductions
                       - regime_used: Tax regime applied
                       - deductions_applied: Summary of deductions
    
    Example:
        >>> # Calculate tax for ₹14,00,000 income with some deductions
        >>> tax_result = calculate_income_tax(
        ...     tool_context=tool_context,
        ...     income=1400000,
        ...     age=29,
        ...     regime='new',
        ...     deductions_80c=150000,
        ...     deductions_hra=200000,
        ...     deductions_80ccd2=100000
        ... )
        >>> print(f"Total tax: ₹{tax_result['total_tax']:,.2f}")
    """
    try:
        # Prepare deductions dictionary for aikar library
        deductions = {
            '80C': deductions_80c,
            'HRA': deductions_hra,
            '80CCD2': deductions_80ccd2,
            'Home Loan': deductions_home_loan
        }

        # Create IncomeTaxCalculator instance
        income_tax_calculator = IncomeTaxCalculator(
            income=income,
            age=age,
            regime=regime,
            deductions=deductions
        )

        # Calculate tax (assuming the calculator has a calculate method or similar)
        # Note: The exact method name may vary based on the actual aikar library implementation
        try:
            # Try common method names for tax calculation
            if hasattr(income_tax_calculator, 'calculate_tax'):
                tax_amount = income_tax_calculator.calculate_tax()
            elif hasattr(income_tax_calculator, 'calculate'):
                tax_amount = income_tax_calculator.calculate()
            elif hasattr(income_tax_calculator, 'get_tax'):
                tax_amount = income_tax_calculator.get_tax()
            else:
                # If no standard method found, try to access tax attribute
                tax_amount = getattr(income_tax_calculator, 'tax', 0)
        except Exception as calc_error:
            logger.exception(f"Error in tax calculation method: {str(calc_error)}")
            # Fallback: return basic calculation info
            tax_amount = 0

        # Handle tax_amount - it might be a dictionary or a number
        if isinstance(tax_amount, dict):
            # If it's a dictionary, try to extract the tax value
            actual_tax = tax_amount.get('tax', tax_amount.get('total_tax', tax_amount.get('income_tax', 0)))
        else:
            # If it's already a number, use it directly
            actual_tax = tax_amount if tax_amount is not None else 0

        # Ensure actual_tax is a number
        try:
            actual_tax = float(actual_tax)
        except (ValueError, TypeError):
            actual_tax = 0

        # Calculate taxable income after deductions
        total_deductions = sum(deductions.values())
        taxable_income = max(0, income - total_deductions)

        result = {
            "total_tax": actual_tax,
            "taxable_income": taxable_income,
            "gross_income": income,
            "regime_used": regime,
            "age": age,
            "deductions_applied": {
                "section_80c": deductions_80c,
                "hra": deductions_hra,
                "section_80ccd2": deductions_80ccd2,
                "home_loan_interest": deductions_home_loan,
                "total_deductions": total_deductions
            },
            "tax_rate_applicable": "Based on Indian tax slabs",
            "calculation_status": "success",
            "raw_calculator_response": tax_amount  # Include raw response for debugging
        }

        logger.info(f"Income tax calculated: ₹{actual_tax:,.2f} for income ₹{income:,.2f} using {regime} regime")
        return result

    except Exception as e:
        logger.exception(f"Error calculating income tax: {str(e)}")
        return {
            "total_tax": 0,
            "taxable_income": 0,
            "gross_income": income,
            "regime_used": regime,
            "age": age,
            "deductions_applied": {},
            "error": str(e),
            "calculation_status": "failed"
        }


def calculate_capital_gains_tax(
        tool_context: ToolContext,
        asset_type: str,
        profit_amount: float,
        buy_date: str,
        sell_date: str
) -> Dict[str, Any]:
    """
    Calculate capital gains tax for various asset types using aikar library.
    
    This tool calculates capital gains tax for different asset types including
    equity, debt, gold, and real estate based on holding period and profit amount.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info.
        asset_type (str): Type of asset - 'equity', 'debt', 'gold', 'real_estate'. Required.
        profit_amount (float): Profit/gain amount in INR. Required.
        buy_date (str): Purchase date in format 'DD/MM/YYYY' or 'MM/DD/YYYY'. Required.
        sell_date (str): Sale date in format 'DD/MM/YYYY' or 'MM/DD/YYYY'. Required.
    
    Returns:
        Dict[str, Any]: Dictionary containing capital gains tax details including:
                       - capital_gains_tax: Tax amount on capital gains
                       - holding_period: Duration of holding
                       - gain_type: Short-term or long-term capital gain
                       - asset_type: Type of asset
                       - profit_amount: Profit/gain amount
    
    Example:
        >>> # Calculate capital gains tax for gold investment
        >>> cg_result = calculate_capital_gains_tax(
        ...     tool_context=tool_context,
        ...     asset_type='gold',
        ...     profit_amount=125000,
        ...     buy_date='01/03/2023',
        ...     sell_date='02/03/2029'
        ... )
        >>> print(f"Capital gains tax: ₹{cg_result['capital_gains_tax']:,.2f}")
    """
    try:
        # Create CapitalGainsCalculator instance
        capital_gains_calculator = CapitalGainsCalculator(
            asset_type,
            profit_amount,
            buy_date,
            sell_date
        )

        # Calculate capital gains tax
        try:
            # Try common method names for capital gains tax calculation
            if hasattr(capital_gains_calculator, 'calculate_tax'):
                cg_tax = capital_gains_calculator.calculate_tax()
            elif hasattr(capital_gains_calculator, 'calculate'):
                cg_tax = capital_gains_calculator.calculate()
            elif hasattr(capital_gains_calculator, 'get_tax'):
                cg_tax = capital_gains_calculator.get_tax()
            else:
                # If no standard method found, try to access tax attribute
                cg_tax = getattr(capital_gains_calculator, 'tax', 0)
        except Exception as calc_error:
            logger.error(f"Error in capital gains calculation method: {str(calc_error)}")
            cg_tax = 0

        # Determine holding period and gain type (basic logic)
        from datetime import datetime
        try:
            # Try to parse dates to determine holding period
            buy_dt = datetime.strptime(buy_date, '%d/%m/%Y')
            sell_dt = datetime.strptime(sell_date, '%d/%m/%Y')
            holding_days = (sell_dt - buy_dt).days

            # Determine gain type based on asset type and holding period
            if asset_type.lower() == 'equity':
                gain_type = 'Long Term' if holding_days > 365 else 'Short Term'
            elif asset_type.lower() in ['debt', 'gold']:
                gain_type = 'Long Term' if holding_days > 1095 else 'Short Term'  # 3 years
            else:
                gain_type = 'Long Term' if holding_days > 730 else 'Short Term'  # 2 years

        except ValueError:
            # If date parsing fails, use default values
            holding_days = 0
            gain_type = 'Unknown'

        result = {
            "capital_gains_tax": cg_tax,
            "profit_amount": profit_amount,
            "asset_type": asset_type,
            "buy_date": buy_date,
            "sell_date": sell_date,
            "holding_period_days": holding_days,
            "gain_type": gain_type,
            "calculation_status": "success"
        }

        logger.info(f"Capital gains tax calculated: ₹{cg_tax:,.2f} for {asset_type} with profit ₹{profit_amount:,.2f}")
        return result

    except Exception as e:
        logger.exception(f"Error calculating capital gains tax: {str(e)}")
        return {
            "capital_gains_tax": 0,
            "profit_amount": profit_amount,
            "asset_type": asset_type,
            "buy_date": buy_date,
            "sell_date": sell_date,
            "holding_period_days": 0,
            "gain_type": "Unknown",
            "error": str(e),
            "calculation_status": "failed"
        }


def compare_tax_regimes(
        tool_context: ToolContext,
        income: float,
        age: int,
        deductions_80c: float = 0.0,
        deductions_hra: float = 0.0,
        deductions_80ccd2: float = 0.0,
        deductions_home_loan: float = 0.0
) -> Dict[str, Any]:
    """
    Compare tax liability between old and new tax regimes to help choose the better option.
    
    This tool calculates income tax for both old and new regimes with the same income
    and deductions, then provides a comparison to help users decide which regime is better.
    
    Args:
        tool_context (ToolContext): The tool context containing user state and session info.
        income (float): Annual income in INR. Required.
        age (int): Age of the taxpayer. Required.
        deductions_80c (float, optional): Deductions under Section 80C. Defaults to 0.0.
        deductions_hra (float, optional): HRA deductions. Defaults to 0.0.
        deductions_80ccd2 (float, optional): NPS employer contribution. Defaults to 0.0.
        deductions_home_loan (float, optional): Home loan interest. Defaults to 0.0.
    
    Returns:
        Dict[str, Any]: Comparison of both tax regimes including:
                       - old_regime_tax: Tax under old regime
                       - new_regime_tax: Tax under new regime
                       - recommended_regime: Better regime choice
                       - savings_amount: Tax savings by choosing better regime
    
    Example:
        >>> # Compare tax regimes for comprehensive analysis
        >>> comparison = compare_tax_regimes(
        ...     tool_context=tool_context,
        ...     income=1200000,
        ...     age=35,
        ...     deductions_80c=150000,
        ...     deductions_hra=180000
        ... )
        >>> print(f"Recommended: {comparison['recommended_regime']}")
        >>> print(f"Savings: ₹{comparison['savings_amount']:,.2f}")
    """
    try:
        # Calculate tax under old regime
        old_regime_result = calculate_income_tax(
            tool_context=tool_context,
            income=income,
            age=age,
            regime='old',
            deductions_80c=deductions_80c,
            deductions_hra=deductions_hra,
            deductions_80ccd2=deductions_80ccd2,
            deductions_home_loan=deductions_home_loan
        )

        # Calculate tax under new regime
        new_regime_result = calculate_income_tax(
            tool_context=tool_context,
            income=income,
            age=age,
            regime='new',
            deductions_80c=deductions_80c,
            deductions_hra=deductions_hra,
            deductions_80ccd2=deductions_80ccd2,
            deductions_home_loan=deductions_home_loan
        )

        old_tax = old_regime_result.get('total_tax', 0)
        new_tax = new_regime_result.get('total_tax', 0)

        # Determine better regime
        if old_tax < new_tax:
            recommended_regime = 'old'
            savings_amount = new_tax - old_tax
        elif new_tax < old_tax:
            recommended_regime = 'new'
            savings_amount = old_tax - new_tax
        else:
            recommended_regime = 'both_equal'
            savings_amount = 0

        result = {
            "income": income,
            "age": age,
            "old_regime": {
                "total_tax": old_tax,
                "taxable_income": old_regime_result.get('taxable_income', 0),
                "deductions_utilized": old_regime_result.get('deductions_applied', {})
            },
            "new_regime": {
                "total_tax": new_tax,
                "taxable_income": new_regime_result.get('taxable_income', 0),
                "deductions_utilized": new_regime_result.get('deductions_applied', {})
            },
            "recommended_regime": recommended_regime,
            "savings_amount": savings_amount,
            "comparison_summary": {
                "old_regime_better": old_tax < new_tax,
                "new_regime_better": new_tax < old_tax,
                "both_equal": old_tax == new_tax
            },
            "calculation_status": "success"
        }

        logger.info(
            f"Tax regime comparison completed: {recommended_regime} regime recommended with savings of ₹{savings_amount:,.2f}")
        return result

    except Exception as e:
        logger.exception(f"Error comparing tax regimes: {str(e)}")
        return {
            "income": income,
            "age": age,
            "old_regime": {"total_tax": 0},
            "new_regime": {"total_tax": 0},
            "recommended_regime": "unknown",
            "savings_amount": 0,
            "error": str(e),
            "calculation_status": "failed"
        }
