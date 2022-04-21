class ApiException(Exception):
    def __init__(self, title: str, detail: str,
        described_by: str = 'https://google.pt',
        support_id: str = 'https://youtube.com',
        http_code: int = 500) -> None:
        self.title = title
        self.detail = detail
        self.described_by = described_by
        self.support_id = support_id
        self.http_code = http_code

        super().__init__(self.title)