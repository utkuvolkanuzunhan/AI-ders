# AI-ders (short English summary of AGENTS.md, for Antigravity and agy)

This is a rules repository for AI-assisted course tutoring (Turkish). It has no application code. `AGENTS.md` is the single source of rules.

1. **Tutoring chats.** Follow `BASLA.md`: generate your rule packet with `python3 araclar/paket.py --rol <role> --kod <code> --ders <course>` and read it. The packet is the chat's rule set.
2. **Developing the repo.** Keep each rule in one place (`cekirdek/`, `roller/`, `gorevler/`, `secenekler/`, `gorsel/`). Make the smallest change. Add one line per change to `DEGISIKLIKLER.md`.
3. **Test.** `python3 araclar/anlatim_testi.py --kendini-dene` (on Windows add `-X utf8`), then `python3 araclar/uret.py`. Both must finish without errors.
4. **Privacy.** The repo is public: no personal names, e-mails, Drive/chat ids, instructor names, course codes, or instructor material. Personal data stays in the user's local `yerel/` files. Keys live only in environment variables.
5. **Language.** Reports and notes are Turkish. No Turkish characters in file or folder names.
6. **Authority.** Work on a separate branch. No force push. Schema, security, data deletion, release and guard files need approval.
