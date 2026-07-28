# Subdomain-Al-Sinwar 🔍⚡

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-orange?style=for-the-badge" alt="Platform">
</p>

> **Subdomain-Al-Sinwar** هي إطار عمل (Framework) حديث وسريع جداً مخصص لجمع النطاقات الفرعية بشكل غير منفذ (Passive Subdomain Enumeration) بدون إرسال أي طلبات مباشرة للهدف. صُممت الأداة خصيصاً لمختبري الاختراق، باحثي الثغرات (Bug Bounty Hunters)، وفرق الأمن السيبراني.

---

## ✨ المميزات الرئيسية (Key Features)

- ⚡ **محرك غير متزامن (Asynchronous Engine):** يعتمد على `httpx` و `asyncio` لاستعلام عشرات المصادر في نفس الوقت بأقصى سرعة.
- 🎯 **بدون أثر (100% Passive):** لا تتفاعل مباشرة مع الهدف، بل تجمع البيانات من مصادر الاستخبارات المفتوحة (OSINT) وسجلات الشهادات (CT Logs).
- 🛡️ **حفظ البيانات عند المقاطعة (SIGINT Safe):** لو ضغطت `Ctrl+C` في أي وقت، الأداة هتحفظ كل النتائج المجمعة فوراً ولن تفقد أي داتا.
- 📊 **نظام التقييم والأدلة (Evidence & Confidence Scoring):** كل نطاق فرعي يتم ربطه بدليل الاكتشاف وزيادة نسبة الثقة فيه كلما ظهر في أكثر من مصدر.
- 🔄 **إلغاء التكرار التلقائي (Deduplication):** فرز وتصفية النتائج المكررة تلقائياً.
- 🔑 **إدارة المفاتيح والمرونة:** تعمل بمصادر مجانية وتتوسع تلقائياً عند إضافة مفاتيح الـ APIs في ملف `.env`.

---

## 🌐 المصادر المدعومة (Supported Sources)

تعتمد الأداة على مجموعة واسعة من مصادر الاستخبارات المفتوحة مقسمة حسب المستويات:

### 🟢 مصادر مجانية (Free - No API Key Required)
| المصدر | نوع الاستعلام |
| :--- | :--- |
| **crt.sh** | Certificate Transparency Logs |
| **AlienVault OTX** | Open Threat Exchange Passive DNS |
| **RapidDNS** | Fast Subdomain Database Search |
| **Wayback Machine** | Internet Archive CDX Database |
| **Anubis** | Domain Intelligence Database |
| **HackerTarget** | Host Search & IP Mapping |
| **ThreatCrowd** | Threat Intelligence Graphs |
| **DuckDuckGo** | Search Engine Indexing |

### 🔑 مصادر متقدمة (Require API Keys in `.env`)
| المصدر | نوع المفتاح المطلوب |
| :--- | :--- |
| **VirusTotal** | `VIRUSTOTAL_API_KEY` |
| **SecurityTrails** | `SECURITYTRAILS_API_KEY` |
| **Shodan** | `SHODAN_API_KEY` |
| **URLScan** | `URLSCAN_API_KEY` |
| **FOFA** | `FOFA_EMAIL` & `FOFA_KEY` |
| **GitHub Search** | `GITHUB_TOKEN` |

---

## 🛠️ شرح التثبيت (Installation)

### 1️⃣ التثبيت المباشر عبر `pip` (الطريقة الأسهل)

تقدر تثبت الأداة بضغط زر واحدة من GitHub وتشتغل فوراً كـ Command في النظام:

```bash
pip install git+[https://github.com/Mohamed701-call/Subdomain-Al-Sinwar.git](https://github.com/Mohamed701-call/Subdomain-Al-Sinwar.git)
