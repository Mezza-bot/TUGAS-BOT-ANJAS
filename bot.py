import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime


# ==========================================
# KONFIGURASI BOT
# ==========================================

TOKEN = os.getenv("DISCORD_TOKEN")

COMMAND_PREFIX = "!"

FILE_TUGAS = "tugas.json"
FILE_SETTING = "setting.json"


# ==========================================
# INTENTS
# ==========================================

intents = discord.Intents.default()
intents.message_content = True


# ==========================================
# MEMBUAT BOT
# ==========================================

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents
)


# ==========================================
# MEMBUAT FILE DATABASE
# ==========================================

def buat_file_database():

    # FILE TUGAS
    if not os.path.exists(FILE_TUGAS):

        with open(
            FILE_TUGAS,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4,
                ensure_ascii=False
            )


    # FILE SETTING
    if not os.path.exists(FILE_SETTING):

        with open(
            FILE_SETTING,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "channel_reminder": None
                },
                file,
                indent=4
            )


# ==========================================
# MEMBACA TUGAS
# ==========================================

def baca_tugas():

    try:

        with open(
            FILE_TUGAS,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return []


# ==========================================
# MENYIMPAN TUGAS
# ==========================================

def simpan_tugas(data):

    with open(
        FILE_TUGAS,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# MEMBACA SETTING
# ==========================================

def baca_setting():

    try:

        with open(
            FILE_SETTING,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return {
            "channel_reminder": None
        }


# ==========================================
# MENYIMPAN SETTING
# ==========================================

def simpan_setting(data):

    with open(
        FILE_SETTING,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# BOT ONLINE
# ==========================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"🤖 Bot berhasil login sebagai: {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print("🟢 Status: ONLINE")
    print("=" * 50)


    if not cek_deadline.is_running():

        cek_deadline.start()


# ==========================================
# COMMAND PING
# ==========================================

@bot.command()
async def ping(ctx):

    await ctx.send(
        "🏓 Pong! Bot sedang online 🟢"
    )


# ==========================================
# COMMAND HALO
# ==========================================

@bot.command()
async def halo(ctx):

    await ctx.send(
        f"Halo {ctx.author.mention}! 👋\n"
        "Selamat datang di Bot Tugas Discord 📚🤖"
    )


# ==========================================
# COMMAND BANTUAN
# ==========================================

@bot.command()
async def bantuan(ctx):

    pesan = """

🤖 **BOT TUGAS DISCORD**

📚 **COMMAND TUGAS**

`!tambah_tugas Nama Tugas | DD-MM-YYYY`

Contoh:
`!tambah_tugas Laporan Carding | 15-09-2026`


`!lihat_tugas`

Melihat semua tugas.


`!hapus_tugas Nomor`

Contoh:
`!hapus_tugas 1`


`!selesai Nomor`

Contoh:
`!selesai 1`


`!belum_selesai`

Melihat tugas yang belum selesai.


📅 **DEADLINE**

`!deadline`

Melihat deadline terdekat.


🔔 **REMINDER**

`!set_channel`

Mengatur channel reminder.


📊 **STATISTIK**

`!statistik`

Melihat statistik tugas.


🤖 **LAINNYA**

`!ping`

`!halo`

`!bantuan`

"""

    await ctx.send(pesan)


# ==========================================
# SET CHANNEL REMINDER
# ==========================================

@bot.command()
async def set_channel(ctx):

    setting = baca_setting()

    setting["channel_reminder"] = ctx.channel.id

    simpan_setting(setting)


    await ctx.send(

        "✅ **Channel Reminder Berhasil Disimpan!**\n\n"

        "🔔 Reminder tugas akan dikirim "
        "ke channel ini."

    )


# ==========================================
# TAMBAH TUGAS
# ==========================================

@bot.command()
async def tambah_tugas(ctx, *, input_tugas):

    try:

        bagian = input_tugas.split("|")

        if len(bagian) != 2:

            raise ValueError


        tugas = bagian[0].strip()

        deadline = bagian[1].strip()


        # VALIDASI TANGGAL
        datetime.strptime(
            deadline,
            "%d-%m-%Y"
        )


    except ValueError:

        await ctx.send(

            "❌ **Format salah!**\n\n"

            "Gunakan:\n"

            "`!tambah_tugas Nama Tugas | DD-MM-YYYY`\n\n"

            "Contoh:\n"

            "`!tambah_tugas Laporan Carding | 15-09-2026`"

        )

        return


    data = baca_tugas()


    # TAMBAHKAN DATA
    tugas_baru = {

        "tugas": tugas,

        "deadline": deadline,

        "status": "Belum Selesai",

        "reminder_3_hari": False,

        "reminder_1_hari": False,

        "reminder_hari_ini": False

    }


    data.append(
        tugas_baru
    )


    simpan_tugas(data)


    await ctx.send(

        f"✅ **Tugas Berhasil Ditambahkan!**\n\n"

        f"📚 Tugas: {tugas}\n"

        f"📅 Deadline: {deadline}\n"

        f"📌 Status: Belum Selesai"

    )


# ==========================================
# LIHAT SEMUA TUGAS
# ==========================================

@bot.command()
async def lihat_tugas(ctx):

    data = baca_tugas()


    if not data:

        await ctx.send(
            "📭 Belum ada tugas."
        )

        return


    daftar = "📚 **DAFTAR TUGAS**\n\n"


    for i, item in enumerate(
        data,
        start=1
    ):

        status = item.get(
            "status",
            "Belum Selesai"
        )

        deadline = item.get(
            "deadline",
            "-"
        )


        if status == "Selesai":

            emoji = "✅"

        else:

            emoji = "⏳"


        daftar += (

            f"{emoji} **{i}. {item['tugas']}**\n"

            f"📅 Deadline: {deadline}\n"

            f"📌 Status: {status}\n\n"

        )


    await ctx.send(daftar)


# ==========================================
# HAPUS TUGAS
# ==========================================

@bot.command()
async def hapus_tugas(ctx, nomor: int):

    data = baca_tugas()


    if nomor < 1 or nomor > len(data):

        await ctx.send(
            "❌ Nomor tugas tidak ditemukan."
        )

        return


    tugas_dihapus = data.pop(
        nomor - 1
    )


    simpan_tugas(data)


    await ctx.send(

        "🗑️ **Tugas Berhasil Dihapus!**\n\n"

        f"📚 {tugas_dihapus['tugas']}"

    )


# ==========================================
# SELESAIKAN TUGAS
# ==========================================

@bot.command()
async def selesai(ctx, nomor: int):

    data = baca_tugas()


    if nomor < 1 or nomor > len(data):

        await ctx.send(
            "❌ Nomor tugas tidak ditemukan."
        )

        return


    data[nomor - 1]["status"] = "Selesai"


    simpan_tugas(data)


    await ctx.send(

        "🎉 **Tugas Berhasil Diselesaikan!**\n\n"

        f"📚 {data[nomor - 1]['tugas']}"

    )


# ==========================================
# TUGAS BELUM SELESAI
# ==========================================

@bot.command()
async def belum_selesai(ctx):

    data = baca_tugas()

    daftar = []


    for i, item in enumerate(
        data,
        start=1
    ):

        if item.get("status") != "Selesai":

            daftar.append(

                f"⏳ **{i}. {item['tugas']}**\n"

                f"📅 Deadline: "
                f"{item.get('deadline', '-')}"

            )


    if not daftar:

        await ctx.send(
            "🎉 Semua tugas sudah selesai!"
        )

        return


    hasil = (

        "📚 **TUGAS BELUM SELESAI**\n\n"

        + "\n\n".join(daftar)

    )


    await ctx.send(hasil)


# ==========================================
# DEADLINE TERDEKAT
# ==========================================

@bot.command()
async def deadline(ctx):

    data = baca_tugas()

    tugas_aktif = []

    hari_ini = datetime.now().date()


    for i, item in enumerate(
        data,
        start=1
    ):

        if item.get("status") == "Selesai":

            continue


        try:

            tanggal = datetime.strptime(

                item["deadline"],

                "%d-%m-%Y"

            ).date()


            sisa_hari = (
                tanggal - hari_ini
            ).days


            tugas_aktif.append({

                "nomor": i,

                "tugas": item["tugas"],

                "deadline": item["deadline"],

                "tanggal": tanggal,

                "sisa_hari": sisa_hari

            })


        except ValueError:

            continue


    if not tugas_aktif:

        await ctx.send(
            "🎉 Tidak ada tugas aktif!"
        )

        return


    tugas_aktif.sort(
        key=lambda x: x["tanggal"]
    )


    tugas = tugas_aktif[0]

    sisa = tugas["sisa_hari"]


    if sisa < 0:

        status = (
            f"❌ Terlambat {abs(sisa)} hari"
        )

    elif sisa == 0:

        status = (
            "🚨 DEADLINE HARI INI!"
        )

    elif sisa == 1:

        status = (
            "⚠️ Deadline Besok!"
        )

    else:

        status = (
            f"⏳ Sisa {sisa} hari"
        )


    await ctx.send(

        "📅 **DEADLINE TERDEKAT**\n\n"

        f"📚 Tugas: {tugas['tugas']}\n"

        f"📅 Deadline: {tugas['deadline']}\n"

        f"{status}"

    )


# ==========================================
# STATISTIK TUGAS
# ==========================================

@bot.command()
async def statistik(ctx):

    data = baca_tugas()


    total = len(data)


    selesai_jumlah = sum(

        1

        for item in data

        if item.get("status") == "Selesai"

    )


    belum_jumlah = (
        total - selesai_jumlah
    )


    if total > 0:

        progress = (
            selesai_jumlah / total
        ) * 100

    else:

        progress = 0


    await ctx.send(

        "📊 **STATISTIK TUGAS**\n\n"

        f"📚 Total Tugas: {total}\n"

        f"✅ Selesai: {selesai_jumlah}\n"

        f"⏳ Belum Selesai: {belum_jumlah}\n"

        f"📈 Progress: {progress:.1f}%"

    )


# ==========================================
# REMINDER OTOMATIS
# ==========================================

@tasks.loop(minutes=30)
async def cek_deadline():

    setting = baca_setting()

    channel_id = setting.get(
        "channel_reminder"
    )


    if channel_id is None:

        return


    channel = bot.get_channel(
        channel_id
    )


    if channel is None:

        return


    data = baca_tugas()

    hari_ini = datetime.now().date()

    ada_perubahan = False


    for item in data:


        # LEWATI TUGAS SELESAI
        if item.get("status") == "Selesai":

            continue


        try:

            tanggal_deadline = datetime.strptime(

                item["deadline"],

                "%d-%m-%Y"

            ).date()


        except ValueError:

            continue


        sisa_hari = (

            tanggal_deadline - hari_ini

        ).days


        # ==================================
        # REMINDER 3 HARI
        # ==================================

        if (

            sisa_hari == 3

            and not item.get(
                "reminder_3_hari",
                False
            )

        ):

            await channel.send(

                "🔔 **REMINDER TUGAS**\n\n"

                f"📚 Tugas: {item['tugas']}\n"

                f"📅 Deadline: "
                f"{item['deadline']}\n"

                "⏳ Sisa waktu: 3 Hari"

            )


            item[
                "reminder_3_hari"
            ] = True


            ada_perubahan = True


        # ==================================
        # REMINDER 1 HARI
        # ==================================

        elif (

            sisa_hari == 1

            and not item.get(
                "reminder_1_hari",
                False
            )

        ):

            await channel.send(

                "⚠️ **DEADLINE BESOK!**\n\n"

                f"📚 Tugas: {item['tugas']}\n"

                f"📅 Deadline: "
                f"{item['deadline']}\n"

                "⏳ Sisa waktu: 1 Hari"

            )


            item[
                "reminder_1_hari"
            ] = True


            ada_perubahan = True


        # ==================================
        # REMINDER HARI INI
        # ==================================

        elif (

            sisa_hari == 0

            and not item.get(
                "reminder_hari_ini",
                False
            )

        ):

            await channel.send(

                "🚨 **DEADLINE HARI INI!**\n\n"

                f"📚 Tugas: {item['tugas']}\n"

                f"📅 Deadline: "
                f"{item['deadline']}\n"

                "⚠️ Segera selesaikan tugas!"

            )


            item[
                "reminder_hari_ini"
            ] = True


            ada_perubahan = True


    # SIMPAN JIKA ADA PERUBAHAN
    if ada_perubahan:

        simpan_tugas(data)


# ==========================================
# BOT SIAP SEBELUM REMINDER
# ==========================================

@cek_deadline.before_loop
async def sebelum_cek_deadline():

    await bot.wait_until_ready()


# ==========================================
# ERROR HANDLER
# ==========================================

@bot.event
async def on_command_error(ctx, error):


    if isinstance(
        error,
        commands.CommandNotFound
    ):

        await ctx.send(

            "❌ Command tidak ditemukan.\n\n"

            "Gunakan `!bantuan` "
            "untuk melihat daftar command."

        )


    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(

            "❌ Data belum lengkap.\n\n"

            "Gunakan `!bantuan` "
            "untuk melihat cara penggunaan."

        )


    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "❌ Format input salah."
        )


    else:

        print(
            f"ERROR: {error}"
        )


# ==========================================
# JALANKAN BOT
# ==========================================

if __name__ == "__main__":


    # BUAT DATABASE
    buat_file_database()


    # CEK TOKEN
    if not TOKEN:

        print(
            "❌ DISCORD_TOKEN belum diatur!"
        )

        print(
            "Buat Environment Variable:"
        )

        print(
            "DISCORD_TOKEN=TOKEN_BOT_KAMU"
        )


    else:

        print(
            "🚀 Menjalankan Bot..."
        )

        bot.run(TOKEN)