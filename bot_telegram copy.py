import os
import datetime
from telegram import Update #type: ignore
from telegram.ext import ( #type: ignore
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)

# Definindo os estados da conversa
PRIMEIRA_MENSAGEM, NOME, CELULAR, PEDIDO, CONFIRMACAO = range(5)

TOKEN = ''  # token do seu bot

# Função para iniciar a conversa e aguardar a primeira mensagem
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Olá! Eu sou o *Barbosa_bot* 🤖.\n\n'
        'Como posso ajudar hoje? Por favor, envie qualquer mensagem para começarmos o atendimento.',
        parse_mode='Markdown'
    )
    return PRIMEIRA_MENSAGEM

# Função para capturar a primeira mensagem do cliente e pedir o nome
async def primeira_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Que bom que você entrou em contato! 😊\n\n'
        'Para melhor atendê-lo, por favor, informe o seu *nome*.',
        parse_mode='Markdown'
    )
    return NOME

# Função para capturar o nome e pedir o número de celular
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip()
    context.user_data['nome'] = user_name
    await update.message.reply_text(
        f'Prazer em conhecê-lo, *{user_name}*! 📱\n\n'
        'Agora, poderia me informar seu número de celular com DDD?',
        parse_mode='Markdown'
    )
    return CELULAR

# Função para capturar o número de celular e pedir o pedido
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()
    context.user_data['celular'] = phone_number
    await update.message.reply_text(
        'Perfeito! 📝\n\n'
        'Por favor, me diga qual é o seu *pedido* ou como posso te ajudar?',
        parse_mode='Markdown'
    )
    return PEDIDO

# Função para capturar o pedido e solicitar confirmação
async def get_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pedido = update.message.text.strip()
    context.user_data['pedido'] = pedido

    user_name = context.user_data['nome']
    phone_number = context.user_data['celular']

    # Formatar a confirmação dos dados
    confirmation_message = (
        f'*Confirmação dos Dados:*\n\n'
        f'📛 *Nome:* {user_name}\n'
        f'📱 *Celular:* {phone_number}\n'
        f'📝 *Pedido:* {pedido}\n\n'
        'Esses dados estão corretos? (Responda com *sim* ou *não*)'
    )

    await update.message.reply_text(confirmation_message, parse_mode='Markdown')
    return CONFIRMACAO

# Função para salvar os dados após confirmação
async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = update.message.text.strip().lower()

    if resposta == 'sim':
        user_name = context.user_data['nome']
        phone_number = context.user_data['celular']
        pedido = context.user_data['pedido']

        # Definindo o caminho para a pasta 'pedidos'
        pasta_pedidos = 'pedidos'

        # Criar a pasta se ela não existir
        if not os.path.exists(pasta_pedidos):
            os.makedirs(pasta_pedidos)

        # Obter a data atual para incluir no nome do arquivo
        data_atual = datetime.datetime.now().strftime('%Y-%m-%d')
        # Opcional: incluir hora para ter arquivos únicos por pedido
        # data_atual = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Definindo o caminho completo do arquivo com a data no nome
        nome_arquivo = f'clientes_{data_atual}.txt'
        caminho_arquivo = os.path.join(pasta_pedidos, nome_arquivo)

        # Salvar nome, telefone e pedido num arquivo txt com codificação UTF-8
        with open(caminho_arquivo, 'a', encoding='utf-8') as f:
            f.write(f'Nome: {user_name}, Telefone: {phone_number}, Pedido: {pedido}\n')

        await update.message.reply_text(
            f'Obrigado, *{user_name}*! 🙏\n\n'
            f'Seu pedido foi anotado com sucesso! Entraremos em contato pelo número *{phone_number}*. 📞\n\n'
            f'*Agradecemos pela sua preferência!* 😊',
            parse_mode='Markdown'
        )
    elif resposta == 'não':
        await update.message.reply_text(
            'Parece que houve um erro nas informações. Vamos tentar novamente. Por favor, envie /start para reiniciar o atendimento.\n\n'
            '*Agradecemos pela sua preferência!* 😊',
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            'Resposta inválida. Por favor, responda com *sim* ou *não*.',
            parse_mode='Markdown'
        )
        return CONFIRMACAO  # Permite ao usuário tentar novamente

    return ConversationHandler.END

# Função para cancelar o atendimento
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Atendimento cancelado. Se precisar de mais alguma coisa, é só chamar! 😃\n\n'
        '*Agradecemos pela sua preferência!* 😊',
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# Função para fornecer ajuda
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Aqui estão os comandos disponíveis:\n"
        "/start - Iniciar o bot\n"
        "/help - Mostrar este menu de ajuda\n"
        "Envie qualquer mensagem de texto para começar o atendimento."
    )
    await update.message.reply_text(help_text)

# Função principal para configurar e iniciar o bot
def main():
    # Criando a aplicação e definindo o token
    app = ApplicationBuilder().token(TOKEN).build()

    # Definindo a conversa para capturar nome, telefone e pedido
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PRIMEIRA_MENSAGEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, primeira_mensagem)],
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CELULAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PEDIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order)],
            CONFIRMACAO: [MessageHandler(filters.Regex('^(sim|não)$'), save_data)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Adicionando os handlers
    app.add_handler(conv_handler)

    # Definindo o handler para o comando /help
    app.add_handler(CommandHandler('help', help_command))

    # Iniciar o bot
    app.run_polling()

# Executar o bot
if __name__ == '__main__':
    main()
