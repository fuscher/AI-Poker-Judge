"""Command-line interface
命令行交互界面"""

from .config import (
    MODEL_A_NAME, MODEL_A_API_KEY, MODEL_A_BASE_URL,
    MODEL_B_NAME, MODEL_B_API_KEY, MODEL_B_BASE_URL,
    DEFAULT_ROUNDS, DEFAULT_SEED, BLACKBOX_WORKERS,
    TIMEOUT_SECONDS, POSITION_SWAP, DEAL_NORMALIZATION
)
from .i18n import t, toggle_lang
from .model.client import ModelClient
from .runner.batch_runner import BatchRunner
from .runner.visual_runner import run_visual_mode
from .runner.blackbox_runner import run_blackbox_mode
from .report.generator import save_report


session_config = {}


def _mask_key(key: str) -> str:
    if not key:
        return "(not set)"
    if len(key) > 8:
        return key[:4] + "···" + key[-4:]
    return "***"


def _load_session_config():
    session_config.clear()
    session_config.update({
        "a_name": MODEL_A_NAME, "a_key": MODEL_A_API_KEY, "a_url": MODEL_A_BASE_URL,
        "b_name": MODEL_B_NAME, "b_key": MODEL_B_API_KEY, "b_url": MODEL_B_BASE_URL,
        "rounds": DEFAULT_ROUNDS, "workers": BLACKBOX_WORKERS,
        "position_swap": POSITION_SWAP, "deal_normalization": DEAL_NORMALIZATION,
        "timeout": TIMEOUT_SECONDS, "seed": DEFAULT_SEED,
    })


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
                                                                              
                █████╗ ██╗██████╗  ██████╗ ██╗  ██╗███████╗██████╗                         
               ██╔══██╗██║██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗                        
               ███████║██║██████╔╝██║   ██║█████╔╝ █████╗  ██████╔╝                        
               ██╔══██║██║██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗                        
               ██║  ██║██║██║     ╚██████╔╝██║  ██╗███████╗██║  ██║                       
               ╚═╝  ╚═╝╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                        
                                                                                                                                      
                           AI vs AI · Poker Arena 🃟                                
                                                                               
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_menu():
    print("\n" + "=" * 79)
    print(t("menu_title"))
    print("  1.  " + t("menu_dealer"))
    print("  2.  " + t("menu_benchmark"))
    print("  3.  " + t("menu_config"))
    print("  4.  " + t("menu_lang"))
    print("  0.  " + t("menu_exit"))
    print("=" * 79)


def config_menu():
    models_changed = False

    while True:
        sc = session_config
        en = lambda v: t("cfg_enabled") if v else t("cfg_disabled")

        print("\n" + "=" * 79)
        print("            {}  {}".format("⚙️", t("cfg_title")))
        print("=" * 79)
        print("  ── {} ──".format(t("cfg_model_a")))
        print(f"  [1] {t('cfg_name')}:   {sc['a_name']}")
        print(f"  [2] {t('cfg_key')}:    {_mask_key(sc['a_key'])}")
        print(f"  [3] {t('cfg_url')}:    {sc['a_url']}")
        print("  ── {} ──".format(t("cfg_model_b")))
        print(f"  [4] {t('cfg_name')}:   {sc['b_name']}")
        print(f"  [5] {t('cfg_key')}:    {_mask_key(sc['b_key'])}")
        print(f"  [6] {t('cfg_url')}:    {sc['b_url']}")
        print("  ── {} ──".format(t("cfg_game_params")))
        print(f"  [7] {t('cfg_rounds')}:   {sc['rounds']}")
        print(f"  [8] {t('cfg_workers')}:   {sc['workers']}")
        print(f"  [9] {t('cfg_position_swap')}: {en(sc['position_swap'])}")
        print(f"  [10] {t('cfg_deal_norm')}: {en(sc['deal_normalization'])}")
        print(f"  [11] {t('cfg_timeout')}:   {sc['timeout']}{t('cfg_timeout_s')}")
        print(f"  [12] {t('cfg_seed')}:   {sc['seed']} (None={t('cfg_random')})")
        print("  " + "-" * 75)
        print("  [C] {}".format(t("cfg_check_conn")))
        print("  [0] {}".format(t("cfg_return")))
        print("=" * 79)

        choice = input("  {} ".format(t("cfg_enter_option"))).strip()

        if choice == "0":
            break
        elif choice.upper() == "C":
            print()
            check_models()
        elif choice == "1":
            v = input("  {} ".format(t("cfg_prompt_name", label="A", cur=sc['a_name']))).strip()
            if v: sc["a_name"] = v; models_changed = True
        elif choice == "2":
            v = input("  {} ".format(t("cfg_prompt_key", label="A", cur=_mask_key(sc['a_key'])))).strip()
            if v: sc["a_key"] = v; models_changed = True
        elif choice == "3":
            v = input("  {} ".format(t("cfg_prompt_url", label="A", cur=sc['a_url']))).strip()
            if v: sc["a_url"] = v; models_changed = True
        elif choice == "4":
            v = input("  {} ".format(t("cfg_prompt_name", label="B", cur=sc['b_name']))).strip()
            if v: sc["b_name"] = v; models_changed = True
        elif choice == "5":
            v = input("  {} ".format(t("cfg_prompt_key", label="B", cur=_mask_key(sc['b_key'])))).strip()
            if v: sc["b_key"] = v; models_changed = True
        elif choice == "6":
            v = input("  {} ".format(t("cfg_prompt_url", label="B", cur=sc['b_url']))).strip()
            if v: sc["b_url"] = v; models_changed = True
        elif choice == "7":
            try:
                v = input("  {} ".format(t("cfg_prompt_rounds", cur=sc['rounds']))).strip()
                if v:
                    v = int(v)
                    if v > 0: sc["rounds"] = v
            except ValueError:
                print("  ⚠️ {}".format(t("cfg_invalid_input")))
        elif choice == "8":
            try:
                v = input("  {} ".format(t("cfg_prompt_workers", cur=sc['workers']))).strip()
                if v:
                    v = int(v)
                    if v > 0: sc["workers"] = v
            except ValueError:
                print("  ⚠️ {}".format(t("cfg_invalid_input")))
            if sc["workers"] > sc["rounds"]:
                print(f"  ⚠️ 线程数({sc['workers']})大于轮次({sc['rounds']})，运行时将自动截断")
        elif choice == "9":
            sc["position_swap"] = not sc["position_swap"]
        elif choice == "10":
            sc["deal_normalization"] = not sc["deal_normalization"]
        elif choice == "11":
            try:
                v = input("  {} ".format(t("cfg_prompt_timeout", cur=sc['timeout']))).strip()
                if v:
                    v = int(v)
                    if v > 0: sc["timeout"] = v; models_changed = True
            except ValueError:
                print("  ⚠️ {}".format(t("cfg_invalid_input")))
        elif choice == "12":
            v = input("  {} ".format(t("cfg_prompt_seed", cur=sc['seed']))).strip().lower()
            if v == "r":
                sc["seed"] = None
            elif v:
                try:
                    sc["seed"] = int(v)
                except ValueError:
                    print("  ⚠️ {}".format(t("cfg_invalid_input")))
        else:
            print("  ⚠️ {}".format(t("invalid_option")))

    return models_changed


def check_models():
    sc = session_config
    if not sc["a_key"]:
        print("\n⚠️  {}".format(t("check_no_key")))
        return None, None

    model_a = ModelClient(sc["a_name"], sc["a_key"], sc["a_url"], sc["timeout"])
    model_b = ModelClient(sc["b_name"], sc["b_key"] or sc["a_key"], sc["b_url"], sc["timeout"])

    for label, model in [("A", model_a), ("B", model_b)]:
        print("🔍 " + t("check_testing", label=label, name=model.model_name), end=" ")
        if model.check_connection():
            print("\r" + t("check_ok", label=label, name=model.model_name) + "    ")
        else:
            print("\r" + t("check_fail", label=label, name=model.model_name) + "    ")
            return None, None

    return model_a, model_b


def get_rounds():
    try:
        default = session_config.get("rounds", DEFAULT_ROUNDS)
        rounds = input(t("rounds_prompt", default=default)).strip()
        if not rounds:
            return default
        rounds = int(rounds)
        if rounds <= 0:
            return default
        if rounds > 500:
            confirm = input(t("rounds_confirm", n=rounds)).strip().lower()
            if confirm != 'y':
                return get_rounds()
        return rounds
    except ValueError:
        return session_config.get("rounds", DEFAULT_ROUNDS)


def get_seed():
    use_seed = input(t("seed_ask")).strip().lower()
    if use_seed == 'y':
        default = session_config.get("seed", DEFAULT_SEED)
        try:
            seed = input(t("seed_prompt", default=default)).strip()
            return int(seed) if seed else default
        except ValueError:
            return default
    return None


def check_config_tips():
    if not session_config.get("a_key") and not session_config.get("b_key"):
        print("\n" + "=" * 79)
        print("  " + t("tip_title"))
        print("  " + t("tip_no_key"))
        print("  " + t("tip_guide"))
        print("=" * 79 + "\n")


def main():
    print_banner()
    _load_session_config()
    check_config_tips()

    runner = None

    while True:
        print_menu()
        choice = input(t("menu_prompt")).strip()

        if choice == "0":
            print("\n " + t("goodbye"))
            break

        elif choice == "4":
            print(toggle_lang() + "\n")

        elif choice in ("1", "2"):
            if runner is None:
                model_a, model_b = check_models()
                if model_a is None:
                    print("\n" + t("check_reconfig") + "\n")
                    continue
                runner = BatchRunner(model_a, model_b)

            rounds = get_rounds()
            seed = get_seed()

            if choice == "1":
                result = run_visual_mode(runner, rounds, seed,
                                         do_swap=session_config["position_swap"] or session_config["deal_normalization"])
            else:
                workers = min(session_config["workers"], rounds)
                if workers < session_config["workers"]:
                    print(f"  ⚠️ 线程数从 {session_config['workers']} 自动调整为 {workers}（不超过轮次）")
                result = run_blackbox_mode(runner, rounds, seed,
                                           max_workers=workers,
                                           do_swap=session_config["position_swap"] or session_config["deal_normalization"])

            save_report(result, session_config["a_name"], session_config["b_name"])

        elif choice == "3":
            changed = config_menu()
            if changed:
                model_a, model_b = check_models()
                if model_a is None:
                    runner = None
                    print(t("check_reconfig"))
                else:
                    runner = BatchRunner(model_a, model_b)

        else:
            print("❌ " + t("invalid_option"))


if __name__ == "__main__":
    main()
