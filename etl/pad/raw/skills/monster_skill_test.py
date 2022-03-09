import argparse
import json
import sys
import urllib.request
from typing import Any

from pad.raw import Card, MonsterSkill
from pad.raw.skills.active_skill_info import ALL_ACTIVE_SKILLS, ActiveSkill
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw.skills.ja.active_skill_text import JaASTextConverter
from pad.raw.skills.ja.leader_skill_text import JaLSTextConverter
from pad.raw.skills.ko.active_skill_text import KoASTextConverter
from pad.raw.skills.ko.leader_skill_text import KoLSTextConverter
from pad.raw.skills.leader_skill_info import ALL_LEADER_SKILLS, LeaderSkill
from pad.raw.skills.skill_parser import SkillParser


class DefaultArgs:
    skill_type = None  # The skill_type to show
    monster_id = None  # The monster who's skill to show
    server = 'NA'  # The input server

    # The output languages
    show_en = True
    show_ja = False
    show_ko = False

    url = 'https://d30r6ivozz8w2a.cloudfront.net/raw'  # The URL to pull data from
    filepath = None  # The filepath where JSONs are stored.  Only useful when using this tool offline

    showall = False  # Show all skills, even ones without translations
    showofficial = True  # Show official translations


####################################
parser = argparse.ArgumentParser(description="Extracts PAD API data.", add_help=False)

search_group = parser.add_argument_group("Search")
search_group.add_argument("--skill_type", type=int, help="The skill type to show")
search_group.add_argument("--skill_id", type=int, help="The skill to show.")
search_group.add_argument("--monster_id", type=int, help="The monster whos skill to show.")

settings_group = parser.add_argument_group("Settings")
settings_group.add_argument("--server", default="NA", choices=['NA', 'JP', 'KR'], help="The input server")
settings_group.add_argument("--show_en", action="store_true",
                            help="Whether to show En translations."
                                 " This is defaulted to true if no langauges are selected.")
settings_group.add_argument("--show_ja", action="store_true", help="Whether to show Ja translations")
settings_group.add_argument("--show_ko", action="store_true", help="Whether to show Ko translations")

input_group = parser.add_argument_group("Paths")
input_group.add_argument("--url", default="https://d30r6ivozz8w2a.cloudfront.net/raw",
                         help="The URL where the JSONs are stored. Mutually exclusive with --filepath.")
input_group.add_argument("--filepath", help="The filepath where the JSONs are stored. Mutually exclusive with --url.")

output_group = parser.add_argument_group("Output")
output_group.add_argument("--showall", action="store_true",
                          help="Show all skills with this type rather than just ones with descriptions."
                               " Only useful in skill_type mode")
output_group.add_argument("--hideofficial", action="store_false", dest='showofficial',
                          help="Show official translations")

help_group = parser.add_argument_group("Help")
help_group.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")


def main(args):
    def download_json(filename: str) -> Any:
        if args.filepath is not None:
            with open(f"{args.filepath.rstrip('/')}/{args.server.lower()}/{filename}") as file:
                return json.load(file)
        else:
            with urllib.request.urlopen(f"{args.url.rstrip('/')}/{args.server.lower()}/{filename}") as resp:
                return json.load(resp)

    def print_translations(skill) -> None:
        if isinstance(skill, ActiveSkill):
            if args.show_en:
                print("EN:", skill.text(EnASTextConverter()))
            if args.show_ja:
                print("JA:", skill.text(JaASTextConverter()))
            if args.show_ko:
                print("KO:", skill.text(KoASTextConverter()))
        elif isinstance(skill, LeaderSkill):
            if args.show_en:
                print("EN:", skill.text(EnLSTextConverter()))
            if args.show_ja:
                print("JA:", skill.text(JaLSTextConverter()))
            if args.show_ko:
                print("KO:", skill.text(KoLSTextConverter()))

    if len([o for o in (args.skill_type, args.skill_id, args.monster_id) if o is not None]) != 1:
        raise Exception('you must supply exactly one of skill_type, skill_id, or monster_id')

    if args.server not in ("NA", "JP", "KR"):
        raise Exception('unexpected server:' + args.server)

    if not any((args.show_en, args.show_ja, args.show_ko)):
        args.show_en = True

    all_skills = [MonsterSkill(sid, raw) for sid, raw in enumerate(download_json('download_skill_data.json')['skill'])]

    skill_class = skills = None
    if args.skill_type is not None or args.skill_id is not None:
        skills = skill_class = None
        if args.skill_type is not None:
            skill_class = next((s for s in ALL_ACTIVE_SKILLS + ALL_LEADER_SKILLS if s.skill_type == args.skill_type),
                               None)

            if skill_class is None:
                raise Exception(f'no creator for skill type: {args.skill_type}')

            skills = [skill_class(skill) for skill in all_skills if skill.skill_type == args.skill_type]
        elif args.skill_id is not None:
            try:
                skill = all_skills[args.skill_id]
            except IndexError:
                raise Exception(f"invalid skill id: {args.skill_id}")

            skill_class = next((s for s in ALL_ACTIVE_SKILLS + ALL_LEADER_SKILLS
                                if s.skill_type == skill.skill_type), None)
            if skill_class is None:
                if skill.skill_type == 0:
                    raise Exception(f'invalid skill type. maybe this skill isn\'t out in this server?')
                else:
                    raise Exception(f'no creator for skill type: {skill.skill_type}')
            skills = [skill_class(skill)]

        for c, skill in enumerate(skills):
            if skill.raw_description or args.showall:
                if c != 0:
                    print()
                if skill.name:
                    print(f"Skill #{skill.skill_id}: {skill.name}")
                else:
                    print(f"Skill #{skill.skill_id}")
                print("Raw:", skill.raw_data)
                print_translations(skill)
                if skill.raw_description and args.showofficial:
                    print("Official:", skill.raw_description)

    elif args.monster_id is not None:
        raw = next((c for c in download_json('download_card_data.json')['card']
                    if c[0] == args.monster_id), None)
        if raw is None:
            raise Exception(f"Invalid monster id: {args.monster_id}")

        monster = Card(raw)
        skill_parser = SkillParser().parse(all_skills)

        active_skill = skill_parser.active(monster.active_skill_id)
        leader_skill = skill_parser.leader(monster.leader_skill_id)

        print(f"[{monster.monster_no}] {monster.name}\n")
        if active_skill is not None:
            print(f"Active Skill: {active_skill.name}"
                  f" (ID {active_skill.skill_id}, Type {active_skill.skill_type}, Raw {active_skill.raw_data})\n"
                  f"Translations:")
            print_translations(active_skill)
            if args.showofficial:
                print(f"(Official: {active_skill.raw_description})\n")
            else:
                print()
        else:
            print("Active Skill: None\n")
        if leader_skill is not None:
            print(f"Leader Skill: {leader_skill.name}"
                  f" (ID {leader_skill.skill_id}, Type {leader_skill.skill_type}, Raw {leader_skill.raw_data})")
            print_translations(leader_skill)
            if args.showofficial:
                print(f"(Official: {leader_skill.raw_description})")
        else:
            print("Leader Skill: None")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        args_ = DefaultArgs()
    else:
        args_ = parser.parse_args()
    main(args_)
