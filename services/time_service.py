"""
ROADMAP DO MÓDULO

Versão Atual:

* Fornece horário local formatado.

Próxima Versão:

* Adicionar timezone configurável e formatos por localidade.

Versão Futura:

* Agenda contextual, rotinas e recomendações baseadas em calendário.

Dependências Futuras:

* Google Calendar API, tzdata
"""

# TODO:
# Criar testes com relógio congelado para garantir formato e timezone.
# FIXME:
# O serviço usa timezone local implícito e não permite configurar cidade, região ou idioma.
# IMPROVEMENT:
# Adicionar timezone explícito, formatos por localidade e saudação contextual por período do dia.
# FUTURE:
# Integrar Google Calendar para respostas contextualizadas com agenda e rotina do usuário.
# OPTIMIZATION:
# Cachear formatações curtas quando usadas várias vezes no mesmo ciclo de resposta.
# SECURITY:
# Evitar expor localização/timezone em logs quando perfis multiusuário forem adicionados.


"""Current date and time service."""

from datetime import datetime


class TimeService:
    """Provides formatted local time values."""

    def current_time_text(self) -> str:
        """Return the current local time in HH:MM format."""
        return datetime.now().strftime("%H:%M")
