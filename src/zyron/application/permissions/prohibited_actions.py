from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class ProhibitionReason(StrEnum):
    PASSWORD_ACCESS = "password_access"
    BANKING_ACCESS = "banking_access"
    PAYMENT = "payment"
    SECURITY_BYPASS = "security_bypass"
    PERMANENT_DELETION = "permanent_deletion"
    CREDENTIAL_EXPOSURE = "credential_exposure"
    MALICIOUS_CODE = "malicious_code"
    PRIVACY_VIOLATION = "privacy_violation"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ProhibitedAction:
    reason: ProhibitionReason
    message: str
    matched_term: str | None = None


class ProhibitedActions:
    def __init__(
        self,
        extra_patterns: dict[
            ProhibitionReason,
            Iterable[str],
        ]
        | None = None,
    ) -> None:
        self._patterns = self._build_default_patterns()

        if extra_patterns:
            for reason, patterns in extra_patterns.items():
                self._patterns.setdefault(reason, [])

                self._patterns[reason].extend(
                    self._normalize_text(pattern)
                    for pattern in patterns
                    if isinstance(pattern, str) and pattern.strip()
                )

    def check(
        self,
        action_text: str,
    ) -> ProhibitedAction | None:
        normalized_text = self._normalize_text(action_text)

        if not normalized_text:
            return None

        for reason, patterns in self._patterns.items():
            for pattern in patterns:
                if self._matches_pattern(
                    normalized_text,
                    pattern,
                ):
                    return ProhibitedAction(
                        reason=reason,
                        message=self._build_message(reason),
                        matched_term=pattern,
                    )

        return None

    def is_prohibited(
        self,
        action_text: str,
    ) -> bool:
        return self.check(action_text) is not None

    def validate(
        self,
        action_text: str,
    ) -> None:
        result = self.check(action_text)

        if result is not None:
            raise PermissionError(result.message)

    def get_reason(
        self,
        action_text: str,
    ) -> ProhibitionReason | None:
        result = self.check(action_text)

        if result is None:
            return None

        return result.reason

    def _build_default_patterns(
        self,
    ) -> dict[ProhibitionReason, list[str]]:
        return {
            ProhibitionReason.PASSWORD_ACCESS: [
                "mostrar senha",
                "revelar senha",
                "ler senha",
                "copiar senha",
                "buscar senha",
                "descobrir senha",
                "acessar senha",
                "ver senha salva",
                "abrir gerenciador de senhas",
                "extrair senha",
            ],
            ProhibitionReason.BANKING_ACCESS: [
                "acessar banco",
                "entrar no banco",
                "abrir internet banking",
                "consultar conta bancaria",
                "consultar saldo bancario",
                "ver saldo bancario",
                "acessar conta bancaria",
                "abrir aplicativo do banco",
            ],
            ProhibitionReason.PAYMENT: [
                "fazer pagamento",
                "realizar pagamento",
                "pagar boleto",
                "fazer pix",
                "enviar pix",
                "transferir dinheiro",
                "comprar produto",
                "finalizar compra",
                "confirmar compra",
                "realizar transferencia",
            ],
            ProhibitionReason.SECURITY_BYPASS: [
                "desativar antivirus",
                "desligar antivirus",
                "desativar firewall",
                "desligar firewall",
                "burlar seguranca",
                "ignorar seguranca",
                "remover protecao",
                "desativar protecao",
                "contornar autenticacao",
                "burlar autenticacao",
                "desativar mfa",
                "desativar 2fa",
            ],
            ProhibitionReason.PERMANENT_DELETION: [
                "apagar permanentemente",
                "excluir permanentemente",
                "deletar permanentemente",
                "esvaziar lixeira",
                "apagar sem recuperacao",
                "excluir sem recuperacao",
                "formatar disco",
                "formatar computador",
                "remover todos os arquivos",
            ],
            ProhibitionReason.CREDENTIAL_EXPOSURE: [
                "mostrar token",
                "revelar token",
                "copiar token",
                "mostrar chave de api",
                "revelar chave de api",
                "mostrar credencial",
                "revelar credencial",
                "mostrar segredo",
                "revelar segredo",
                "mostrar private key",
                "copiar private key",
            ],
            ProhibitionReason.MALICIOUS_CODE: [
                "criar malware",
                "criar ransomware",
                "criar virus",
                "roubar dados",
                "capturar senha",
                "keylogger",
                "invadir computador",
                "invadir conta",
                "explorar vulnerabilidade",
            ],
            ProhibitionReason.PRIVACY_VIOLATION: [
                "ler mensagens privadas",
                "ler conversa privada",
                "espionar pessoa",
                "monitorar pessoa",
                "gravar pessoa sem permissao",
                "acessar arquivos de outra pessoa",
                "copiar dados pessoais",
            ],
        }

    def _matches_pattern(
        self,
        text: str,
        pattern: str,
    ) -> bool:
        escaped_pattern = re.escape(pattern)

        return (
            re.search(
                rf"(?<!\w){escaped_pattern}(?!\w)",
                text,
            )
            is not None
        )

    def _build_message(
        self,
        reason: ProhibitionReason,
    ) -> str:
        messages = {
            ProhibitionReason.PASSWORD_ACCESS: (
                "Essa ação foi bloqueada porque envolve acesso ou "
                "exposição de senhas."
            ),
            ProhibitionReason.BANKING_ACCESS: (
                "Essa ação foi bloqueada porque envolve acesso a "
                "informações bancárias."
            ),
            ProhibitionReason.PAYMENT: (
                "Essa ação foi bloqueada porque o ZYRON não pode "
                "realizar compras, pagamentos ou transferências."
            ),
            ProhibitionReason.SECURITY_BYPASS: (
                "Essa ação foi bloqueada porque envolve desativar ou "
                "contornar mecanismos de segurança."
            ),
            ProhibitionReason.PERMANENT_DELETION: (
                "Essa ação foi bloqueada porque pode apagar dados de "
                "forma permanente."
            ),
            ProhibitionReason.CREDENTIAL_EXPOSURE: (
                "Essa ação foi bloqueada porque envolve exposição de "
                "tokens, credenciais ou chaves privadas."
            ),
            ProhibitionReason.MALICIOUS_CODE: (
                "Essa ação foi bloqueada porque pode causar dano, "
                "invasão ou roubo de dados."
            ),
            ProhibitionReason.PRIVACY_VIOLATION: (
                "Essa ação foi bloqueada porque pode violar a "
                "privacidade de outra pessoa."
            ),
            ProhibitionReason.UNKNOWN: (
                "Essa ação foi bloqueada por segurança."
            ),
        }

        return messages.get(
            reason,
            messages[ProhibitionReason.UNKNOWN],
        )

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        if not isinstance(text, str):
            return ""

        normalized = unicodedata.normalize(
            "NFKD",
            text,
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

        normalized = normalized.lower().strip()

        normalized = re.sub(
            r"[^a-z0-9\s_-]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized
