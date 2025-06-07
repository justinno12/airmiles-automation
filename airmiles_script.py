from playwright.sync_api import sync_playwright
import time
import imaplib
import email
import re

EMAIL = "jstnlos@gmail.com"
WACHTWOORD = "c&NmA!z7Dh@Ga63"
ONTVANGER_EMAIL = "justinlos123@gmail.com"
IMAP_WACHTWOORD = "dtlz kxpt vpqj lxik"  # Gmail app-wachtwoord

def haal_verificatiecode_op():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, IMAP_WACHTWOORD)
        status, _ = mail.select('"[Gmail]/Belangrijk"')
        if status != "OK":
            print("❌ Belangrijk-map niet gevonden in mailbox.")
            return None
    except Exception as e:
        print(f"❌ Fout bij openen van IMAP-verbinding: {e}")
        return None

    try:
        result, data = mail.search(None, 'FROM', '"services@mailing.airmiles.nl"')
        mail_ids = data[0].split()
    except Exception as e:
        print("❌ Fout bij zoeken naar e-mail:", e)
        return None

    if not mail_ids:
        print("❌ Geen e-mails van Air Miles gevonden in [Gmail]/Belangrijk.")
        return None

    latest_email_id = mail_ids[-1]
    result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = msg_data[0][1]
    message = email.message_from_bytes(raw_email)

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                tekst = part.get_payload(decode=True).decode()
                break
    else:
        tekst = message.get_payload(decode=True).decode()

    print("📩 Inhoud e-mail:\n", tekst)
    match = re.search(r"Jouw verificatiecode is[:\s]+(\d{6})", tekst)
    if match:
        print("✅ Verificatiecode gevonden:", match.group(1))
        return match.group(1)
    else:
        print("❌ Geen verificatiecode gevonden in e-mail.")
        return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Aangepast: headless modus
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.airmiles.nl/")
    page.wait_for_timeout(2000)

    try:
        cookie_knop = page.locator("div[role='button'] span", has_text="Accepteren")
        cookie_knop.first.click(timeout=7000)
        print("✅ Cookie banner geaccepteerd")
    except:
        print("🟡 Geen cookie banner gevonden of al geaccepteerd")

    page.get_by_role("button", name="Inloggen").first.click()
    page.wait_for_timeout(1500)

    page.fill("input[name='emailAddress']", EMAIL)
    page.fill("input[name='password']", WACHTWOORD)
    page.wait_for_timeout(500)

    try:
        page.get_by_role("button", name="Inloggen").nth(1).click()
        print("✅ Inlogknop succesvol aangeklikt.")
    except:
        print("❌ Inlogknop kon niet worden aangeklikt.")

    page.wait_for_timeout(60000)

    try:
        punten = page.inner_text("div.card-details__label--amount")
        print(f"💰 Aantal punten: {punten}")
    except:
        print("❌ Kon het aantal punten niet uitlezen.")
        browser.close()
        exit()

    if int(punten.strip()) >= 100:
        print("🎯 Je hebt 100 punten of meer. Tijd voor overdracht!")

        page.goto("https://www.airmiles.nl/mijn/zelf-regelen/overboeken/")
        print("🌐 Overdrachtformulier geopend.")
        page.wait_for_timeout(3000)

        try:
            page.fill("#transfer-method--email-address", ONTVANGER_EMAIL)
            print("✅ Ontvanger ingevuld")
        except:
            print("❌ Kon ontvanger niet invullen")

        try:
            alles_knop = page.locator("span.sticker__counter", has_text="Alles")
            alles_knop.click(timeout=8000)
            print("✅ 'Alles' knop aangeklikt.")
        except:
            print("❌ Kon niet op 'Alles' klikken.")

        page.wait_for_timeout(3000)
        try:
            page.locator("button:has-text('Overboeken')").click(timeout=10000)
            print("✅ 'Overboeken' knop geklikt.")
        except:
            print("❌ Kon niet op 'Overboeken' klikken.")

        try:
            page.get_by_text("Ja, ik weet het zeker", exact=True).click(timeout=10000)
            print("✅ Bevestiging uitgevoerd.")
        except:
            print("❌ Kon bevestiging niet voltooien.")

        try:
            page.get_by_text("Verifieer via e-mail", exact=True).click(timeout=10000)
            print("✅ Verificatie via e-mail gestart.")
        except:
            print("❌ Kon 'Verifieer via e-mail' niet klikken.")

        print("⏳ Wacht 60 seconden tot de e-mail is aangekomen...")
        time.sleep(60)

        print("📬 Verificatiecode ophalen uit [Gmail]/Belangrijk...")
        code = haal_verificatiecode_op()
        if code:
            try:
                page.locator("input[name='verificationCode']").fill(code)
                time.sleep(3)
                page.locator("span:has-text('Doorgaan')").click()
                print(f"✅ Verificatiecode gevonden: {code}")
                print("✅ Code ingevoerd en doorgaan geklikt.")
                time.sleep(10)
            except:
                print("❌ Kon verificatiecode niet invullen of doorgaan niet klikken.")
        else:
            print("❌ Geen verificatiecode gevonden in mailbox.")
    else:
        print("ℹ️ Je hebt minder dan 100 punten. Geen actie ondernomen.")

    print("🟦 Script automatisch afgesloten.")
    browser.close()
