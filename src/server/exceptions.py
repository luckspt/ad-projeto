"""
Aplicações Distribuídas - Projeto 3 - server/exceptions.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""


class ApiException(Exception):
    def __init__(self, title: str, detail: str,
                 http_code: int = 500,
                 described_by: str = 'https://youtu.be/71sqkgaUncI',
                 support_id: str = 'https://youtu.be/pRpeEdMmmQ0',) -> None:
        self.title = title
        self.detail = detail
        self.described_by = described_by
        self.support_id = support_id
        self.http_code = http_code

        super().__init__(self.title)
