"""
Aplicações Distribuídas - Projeto 4 - server/exceptions.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""


class ApiException(Exception):
    def __init__(self, title: str, detail: str,
                 http_code: int = 500,
                 described_by: str = 'https://pbs.twimg.com/media/FCU_aMdWUAYlhBm.jpg',
                 support_id: str = 'https://www.receitaslidl.pt/var/site/storage/images/6/8/7/4/594786-1-por-PT/Pao-com-Chourico.jpg',) -> None:
        self.title = title
        self.detail = detail
        self.described_by = described_by
        self.support_id = support_id
        self.http_code = http_code

        super().__init__(self.title)
