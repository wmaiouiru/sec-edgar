from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Any, Dict
from secedgar.parsers.common import FilingValues, FilingValuesParser, FilingXMLParser


@dataclass(frozen=True)
class OfferingSalesAmounts:
    total_offering_amount: int
    total_amount_sold: int
    total_remaining: int
    clarification_of_response: str

    @staticmethod
    def from_text(input_text:str) -> OfferingSalesAmounts:
        parser = FilingXMLParser()
        xml_text = parser.get_xml_text(input_text, 'edgarSubmission')
        offering_sales_amount_text = parser.get_xml_text(xml_text, "offeringSalesAmounts")
        return OfferingSalesAmounts(
            total_offering_amount=int(parser.get_tag_value(offering_sales_amount_text, "totalOfferingAmount")),
            total_amount_sold=int(parser.get_tag_value(offering_sales_amount_text, "totalAmountSold")),
            total_remaining=int(parser.get_tag_value(offering_sales_amount_text, "totalRemaining")),
            clarification_of_response=parser.get_tag_value(offering_sales_amount_text, "clarificationOfResponse"),
        )

@dataclass(frozen=True)
class InvestmentFundInfo:
    investment_fund_type: str
    is_40_act: bool

@dataclass(frozen=True)
class IndustryGroup:
    industry_group_type: str
    investment_fund_info: Optional[InvestmentFundInfo] = None
    @staticmethod
    def from_text(input_text:str) -> IndustryGroup:
        parser = FilingXMLParser()
        xml_text = parser.get_xml_text(input_text, 'edgarSubmission')
        return IndustryGroup(
            industry_group_type=parser.get_tag_value(xml_text, "industryGroupType"),
            investment_fund_info=InvestmentFundInfo(
                investment_fund_type=parser.get_tag_value(xml_text,"investmentFundType"),
                is_40_act=bool(parser.get_tag_value(xml_text, "is40Act"))
            ),
        )

@dataclass
class CompanyData:
    company_conformed_name:str
    central_index_key:str
    irs_number:int
    state_of_incorporation:str
    fiscal_year_end: int
    @staticmethod
    def from_text(input_text:str) -> CompanyData:
        parser = FilingValuesParser()
        return CompanyData(
            company_conformed_name=parser.parse_by_re_line(r"COMPANY CONFORMED NAME:	\s+(.*)", input_text),
            central_index_key=parser.parse_by_re_line(r"CENTRAL INDEX KEY:\s+(.*)", input_text),
            irs_number=parser.parse_by_re_line(r"IRS NUMBER:\s+(.*)", input_text),
            state_of_incorporation=parser.parse_by_re_line(r"STATE OF INCORPORATION:\s+(.*)", input_text),
            fiscal_year_end=parser.parse_by_re_line(r"FISCAL YEAR END:\s+(.*)", input_text),
        )

@dataclass
class FormD:
    company_data: CompanyData
    filing_values: FilingValues
    industry_group: IndustryGroup
    offering_sales_amount: OfferingSalesAmounts
    def to_dict(self) -> Dict[str, Any]:
        return {
            'company_conformed_name':self.company_data.company_conformed_name,
            'central_index_key':self.company_data.central_index_key,
            'irs_number':self.company_data.irs_number,
            'film_number':self.filing_values.film_number,
            'sec_file_number':self.filing_values.sec_file_number,
            'industry_group_type': self.industry_group.industry_group_type,
            'investment_fund_type': self.industry_group.investment_fund_info.investment_fund_type,
            'total_offering_amount':self.offering_sales_amount.total_offering_amount,
            'total_amount_sold':self.offering_sales_amount.total_amount_sold,
            'total_remaining':self.offering_sales_amount.total_remaining,
        }


class FDParser:
    """Utility class to extract actionable data and documents from a single text file.
    Specification: https://www.sec.gov/edgar/filer-information/specifications/form-d-xml-tech-specs
    .. warning::
        The ``FDParser`` class is still experimental. Use with caution.

    .. versionadded:: 0.?.0
    """

    @staticmethod
    def process(doc: str) -> FormD:
        """Process the actionable data of the document.

        Args:
            doc (str): Document from which to extract core data.

        Return:
            data (dict): Tradable buy/sell/gift data from document.

        """
        filing_values=FilingValues.from_text(doc)

        return FormD(
            company_data=CompanyData.from_text(doc),
            filing_values=filing_values,
            industry_group=IndustryGroup.from_text(doc),
            offering_sales_amount = OfferingSalesAmounts.from_text(doc)
        )