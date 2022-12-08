from create_bot import bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.types import CallbackQuery
import init_data
import config
import create_bot
import inspect

router = Router()


def get_needed_menu_from_json(menu_name: str) -> list:
    try:
        inter_dict = init_data.interaction_json
        if any(menu_name in d for d in inter_dict["menus"]):
            for menu in inter_dict["menus"]:
                if menu_name in menu:
                    return menu[menu_name]
        else:
            return []
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# gen_universal_callback_data
def get_universal_callback_data(item: dict) -> str:
    try:
        universal_callback_data = "UCD_" + item['type']
        if item['type'] == "text":
            universal_callback_data += "_" + item['answer']
        elif item['type'] == "menu":
            universal_callback_data += "_" + item['menu_name']
        elif item['type'] == "do":
            universal_callback_data += "_" + item['answer']
        return universal_callback_data
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def form_tlg_menu_items(menu_from_json: list = [], msgs_ids: list = []) -> InlineKeyboardMarkup:
    try:
        builder = InlineKeyboardBuilder()
        for item in menu_from_json:
            builder.row(InlineKeyboardButton(text=item['text'], callback_data=get_universal_callback_data(item)))
        builder.row(InlineKeyboardButton(text="❌", callback_data="delete_msg#" + " ".join(msgs_ids)))
        return InlineKeyboardMarkup(inline_keyboard=builder.export())
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.callback_query(lambda callback_query: callback_query.data[:10] == "delete_msg")
async def process_callback_delete_msg(callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
        ls = callback_query.data.split("#")
        for ids in ls[1].split():
            await bot.delete_message(callback_query.message.chat.id, int(ids))
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.callback_query(lambda callback_query: callback_query.data[:3] == "UCD")
async def universal_callback_response(callback_query: CallbackQuery):
    try:
        cd_ls = callback_query.data.split("_")

        if cd_ls[1] == "menu":
            await bot.send_message(callback_query.from_user.id,
                                   text="<pre>Вы выбрали пункт меню:\n" + init_data.menu_names[cd_ls[2]] + "</pre>",
                                   parse_mode="HTML",
                                   reply_markup=form_tlg_menu_items(get_needed_menu_from_json(cd_ls[2])))
            await callback_query.answer()
        elif cd_ls[1] == "text":
            id1 = await bot.send_message(callback_query.from_user.id,
                                         text=f"<pre>{init_data.answer_names[cd_ls[2]]}</pre>",
                                         parse_mode="HTML")
            await bot.send_message(callback_query.from_user.id, text=init_data.answer_json[cd_ls[2]]["text"],
                                   reply_markup=form_tlg_menu_items(msgs_ids=[str(id1.message_id)]))
            await callback_query.answer()
        elif cd_ls[1] == "do":
            await bot.send_message(callback_query.from_user.id, init_data.answer_json[cd_ls[2]]["text"],
                                   reply_markup=form_tlg_menu_items())
            await callback_query.answer()
            return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    try:
        # регистрируем пользователя в базе
        if not init_data.db.reg_user_exists(message.from_user.id):
            init_data.db.add_reg_user_to_db(message.from_user.id)
        # отдаем пользователю меню
        await message.answer(text="<pre>Начальное меню.\nЧто бы вы хотели?</pre>", parse_mode="HTML",
                             reply_markup=form_tlg_menu_items(get_needed_menu_from_json("menu0")))
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["вступить", "vstupit"]))
async def command_join_handler(message: Message) -> None:
    try:
        # регистрируем пользователя в базе
        if not init_data.db.reg_user_exists(message.from_user.id):
            init_data.db.add_reg_user_to_db(message.from_user.id)

        if init_data.Chek_email_before_join:
            # если проверка почт, проверяем не состоит ли он в канале
            chat_member = await bot.get_chat_member(config.Chanel_Id, message.from_user.id)
            # проверяем находится ли пользователь вне канала
            if chat_member.status == 'left':
                # проверяем что пользователь попытался ввести почту
                if len(message.text.split()) > 1:
                    user_email = message.text.split()[1]
                    # приводим емайл пользователя к нижнему регистру и дальше уже раюотаем с ним
                    user_email = user_email.lower()
                    # проверяем есть ли почта пользователя в разрешенных
                    if user_email in init_data.Email_user_list:
                        # проверяем нет ли уже записи с такой почтой в базе
                        if not init_data.db.user_exists(user_email):
                            # даем ссылку
                            invite_link = await bot.create_chat_invite_link(config.Chanel_Id, member_limit=1)
                            await message.answer(invite_link.invite_link)
                            init_data.db.add_user_to_db(message.from_user.id, user_email)
                        else:
                            # получается что такая почта уже есть в базе, проверяем может этот пользователь уже вышел из группы
                            chat_member2 = await bot.get_chat_member(config.Chanel_Id,
                                                                     init_data.db.get_user_tlg_id(user_email))
                            # если по этой почте регестрировался другой пользователь, проверим не ушел ли он уже из группы
                            if chat_member2.status == "member":
                                # если он не ушел значит что то не так
                                await message.answer(
                                    f"Что то пошло не так..\nПользователь с таким email{user_email} и id {init_data.db.get_user_tlg_id(user_email)} уже состоит в канале.")
                                return
                            else:
                                # если другой пользователь ушел, удаляем старую запись добавляем новую
                                init_data.db.del_user_from_db(init_data.db.get_user_tlg_id(user_email))
                                init_data.db.add_user_to_db(message.from_user.id, user_email)
                                invite_link = await bot.create_chat_invite_link(config.Chanel_Id, member_limit=1)
                                await message.answer(invite_link.invite_link)
                    else:
                        # почты пользователя нет в разрешенныых предлогаем ввести нужную почту
                        await message.answer(
                            f"Что то пошло не так..\nИспользуйте email по которому зарегестрированы в GetCourse \nhttps://lesson.shamilahmadullin.com/")
                        return
                else:
                    # предлагаем пользователю ввести почту
                    await message.answer(
                        "Чтобы попасть в канал напишите в данный чат: \n/вступить [ваш емайл] \n\n Пример: <pre>/вступить ivanov1985@email.ru </pre> ",
                        parse_mode="html")
                    return

            else:
                # получается что пользователь уже в канале или админ
                if chat_member.status == 'member':
                    await message.answer("Что то пошло не так..\nВы уже состоите в закрытом канале РУМ клуба.")
                    return
                if chat_member.status == 'kicked':
                    await message.answer("Что то пошло не так..\nВы были удалены из закрытого канала РУМ клуба.")
                    return
                await message.answer(f"Что то пошло не так..\nВаш статус {chat_member.status}")

        else:
            # если почта не требуется высылаем ссылку всем
            invite_link = await bot.create_chat_invite_link(config.Chanel_Id, member_limit=1)
            await message.answer(invite_link.invite_link)

    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["отзыв", "otziv"]))
async def command_reviev_handler(message: Message) -> None:
    try:
        # регистрируем пользователя в базе
        if not init_data.db.reg_user_exists(message.from_user.id):
            init_data.db.add_reg_user_to_db(message.from_user.id)

        if len(message.text.split()) <= 1:
            await message.answer(
                "Чтобы оставить отзыв или предложение напишите в данный чат: \n/отзыв [ваш отзыв] \n\n Пример: <pre>/отзыв пожалуйста публикуйте расписание мероприятий каждое утро. </pre> ",
                parse_mode="html")
            return

        caption = f"Отзыв от {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name} \n"
        await bot.send_message(config.Reviews_chat_id, caption + message.text[7:])
        await message.reply(
            "Ваш отзыв получен. Спасибо за обратную связь. Отзыв не предполагает обратного ответа. "
            "При необходимости обратитесь в службу поддержки https://lesson.shamilahmadullin.com/cms/system/contact")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
