import pytest
from secedgar.parser import MetaParser, F4Parser
from secedgar.parsers.form_d_parser import FDParser
from secedgar.tests.utils import MockResponse, datapath

class TestParser:
    parser = MetaParser()

    def test_process_document_metadata(self):
        doc = """<TYPE>10-K
        <SEQUENCE>123
        <FILENAME>test-filename.txt
        """
        metadata = self.parser.process_document_metadata(doc)
        assert metadata == {"type": "10-K", "sequence": "123", "filename": "test-filename.txt"}

    @pytest.mark.parametrize(
        "bad_filetype",
        [
            "xml",
            "json",
            "html",
            "txt.gz",
            "zip"
        ]
    )
    def test_bad_filetypes_raises_error(self, bad_filetype):
        with pytest.raises(ValueError):
            self.parser.process(infile="test.{0}".format(bad_filetype))


class TestF4Parser:

    parser = F4Parser()

    def test_process_document_metadata_form_4(self):
        doc = """<TYPE>4
        <SEQUENCE>123
        <FILENAME>test-filename.txt
        <nonDerivativeTable>
        <nonDerivativeTransaction>
            <securityTitle>
                <value>Common Stock</value>
            </securityTitle>
            <transactionDate>
                <value>2021-05-14</value>
            </transactionDate>
            <transactionCoding>
                <transactionFormType>5</transactionFormType>
                <transactionCode>G</transactionCode>
                <equitySwapInvolved>0</equitySwapInvolved>
            </transactionCoding>
            <transactionTimeliness>
                <value>E</value>
            </transactionTimeliness>
            <transactionAmounts>
                <transactionShares>
                    <value>4010</value>
                </transactionShares>
                <transactionPricePerShare>
                    <value>0</value>
                </transactionPricePerShare>
                <transactionAcquiredDisposedCode>
                    <value>D</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
            <postTransactionAmounts>
                <sharesOwnedFollowingTransaction>
                    <value>324164</value>
                </sharesOwnedFollowingTransaction>
            </postTransactionAmounts>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>D</value>
                </directOrIndirectOwnership>
            </ownershipNature>
        </nonDerivativeTransaction>
        <nonDerivativeTransaction>
            <securityTitle>
                <value>Common Stock</value>
                <footnoteId id="F1"/>
            </securityTitle>
            <transactionDate>
                <value>2021-08-02</value>
            </transactionDate>
            <transactionCoding>
                <transactionFormType>4</transactionFormType>
                <transactionCode>S</transactionCode>
                <equitySwapInvolved>0</equitySwapInvolved>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares>
                    <value>15600</value>
                </transactionShares>
                <transactionPricePerShare>
                    <value>145.83</value>
                    <footnoteId id="F2"/>
                </transactionPricePerShare>
                <transactionAcquiredDisposedCode>
                    <value>D</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
            <postTransactionAmounts>
                <sharesOwnedFollowingTransaction>
                    <value>308564</value>
                </sharesOwnedFollowingTransaction>
            </postTransactionAmounts>
            <ownershipNature>
                <directOrIndirectOwnership>
                    <value>D</value>
                </directOrIndirectOwnership>
            </ownershipNature>
        </nonDerivativeTransaction>
    </nonDerivativeTable>
        """
        data = self.parser.process(doc)
        assert data == {
            "nonDerivativeTable": {
                "nonDerivativeTransaction": [
                    {
                        "securityTitle": "Common Stock",
                        "transactionDate": "2021-05-14",
                        "transactionCoding": {
                            "transactionFormType": "5",
                            "transactionCode": "G",
                            "equitySwapInvolved": "0"
                        },
                        "transactionAmounts": {
                            "transactionShares": "4010",
                            "transactionPricePerShare": "0",
                            "transactionAcquiredDisposedCode": "D"
                        },
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": "324164"
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": "D"
                        }
                    },
                    {
                        "securityTitle": "Common Stock",
                        "transactionDate": "2021-08-02",
                        "transactionCoding": {
                            "transactionFormType": "4",
                            "transactionCode": "S",
                            "equitySwapInvolved": "0"
                        },
                        "transactionAmounts": {
                            "transactionShares": "15600",
                            "transactionPricePerShare": "145.83",
                            "transactionAcquiredDisposedCode": "D"
                        },
                        "postTransactionAmounts": {
                            "sharesOwnedFollowingTransaction": "308564"
                        },
                        "ownershipNature": {
                            "directOrIndirectOwnership": "D"
                        }
                    }
                ]
            }
        }

class TestFDParser:
    parser = FDParser()

    def read_text_file(self, filename: str) -> str:
        """ Read text file """
        with open(datapath("filings", "form_d", filename)) as f:
            return f.read()

    def test_process_document_metadata_form_d_sample(self):
        doc = self.read_text_file('SampleFormD.xml')
        form_d = self.parser.process(doc)

        # assert form_d.company_data.central_index_key = ''
        assert form_d.offering_sales_amount.total_offering_amount == 1000
        assert form_d.offering_sales_amount.total_amount_sold == 100
        assert form_d.offering_sales_amount.total_remaining == 900
        assert form_d.offering_sales_amount.clarification_of_response == 'Clarification of Response'

        assert form_d.industry_group.investment_fund_info.investment_fund_type == 'Venture Capital Fund'
        assert form_d.industry_group.investment_fund_info.is_40_act is True

    def test_process_document_metadata_form_d(self):
        doc = self.read_text_file('0001980155-23-000002.txt')
        form_d = self.parser.process(doc)

        # assert form_d.company_data.central_index_key = ''
        assert form_d.offering_sales_amount.total_offering_amount == 111000
        assert form_d.offering_sales_amount.total_amount_sold == 111000
        assert form_d.offering_sales_amount.total_remaining == 0
        assert form_d.offering_sales_amount.clarification_of_response == 'Amounts shown here include totals from the Issuer and a parallel fund of the Issuer.'

        assert form_d.industry_group.investment_fund_info.investment_fund_type == 'Venture Capital Fund'
        assert form_d.industry_group.investment_fund_info.is_40_act is True