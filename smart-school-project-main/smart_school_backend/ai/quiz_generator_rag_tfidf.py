#!/usr/bin/env python3
"""
Simple MCQ generator prototype (rule-based).
Input: paragraph string (or file)
Output: prints 2-3 MCQs (cloze style) with options
Requires: nltk
"""

import sys
import random
import argparse
import nltk
from nltk.corpus import wordnet as wn

# Ensure required corpora (first run may download)
nltk_packages = ["punkt", "averaged_perceptron_tagger", "wordnet", "omw-1.4"]
for pkg in nltk_packages:
    try:
        nltk.data.find(pkg)
    except LookupError:
        nltk.download(pkg)


def extract_noun_candidates(sentence):
    words = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(words)
    # NN, NNS, NNP, NNPS
    nouns = [w for w, p in tagged if p.startswith("NN") and w.isalpha() and len(w) > 3]
    return nouns


def get_distractors_from_wordnet(word, max_distractors=3):
    distractors = set()
    synsets = wn.synsets(word, pos=wn.NOUN)
    for s in synsets:
        for lem in s.lemmas():
            w = lem.name().replace("_", " ")
            if w.lower() != word.lower():
                distractors.add(w)
        # hypernyms/hyponyms
        for h in s.hypernyms() + s.hyponyms():
            for lem in h.lemmas():
                w = lem.name().replace("_", " ")
                if w.lower() != word.lower():
                    distractors.add(w)
        if len(distractors) >= max_distractors:
            break
    return list(distractors)[:max_distractors]


def generate_mcqs(text, num_qs=3):
    sentences = nltk.sent_tokenize(text)
    candidates = [s for s in sentences if len(s.split()) >= 6]
    if not candidates:
        return []

    # collect all nouns in text for distractor reservoir
    all_nouns = []
    for s in candidates:
        all_nouns += extract_noun_candidates(s)
    all_nouns = list(dict.fromkeys(all_nouns))  # preserve order, unique

    mcqs = []
    used_sentences = set()
    random.shuffle(candidates)
    for s in candidates:
        if len(mcqs) >= num_qs:
            break
        if s in used_sentences:
            continue
        nouns = extract_noun_candidates(s)
        if not nouns:
            continue
        # prefer proper nouns or first noun
        answer = nouns[0]
        # build question (cloze)
        question = s.replace(answer, "_____")
        # build distractors
        distractors = []
        # try WordNet
        wn_d = get_distractors_from_wordnet(answer, max_distractors=3)
        for d in wn_d:
            if d.lower() != answer.lower() and d not in distractors:
                distractors.append(d)
        # fallback to other nouns in text
        for n in all_nouns:
            if n.lower() != answer.lower() and n not in distractors:
                distractors.append(n)
            if len(distractors) >= 3:
                break
        # final fallback: random common words
        while len(distractors) < 3:
            cand = "option" + str(random.randint(1,100))
            if cand.lower() != answer.lower() and cand not in distractors:
                distractors.append(cand)
        options = [answer] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(answer)
        mcqs.append({
            "question": question,
            "options": options,
            "answer_index": correct_index
        })
        used_sentences.add(s)

    return mcqs


def print_mcqs(mcqs):
    for i, q in enumerate(mcqs, 1):
        print(f"Q{i}: {q['question']}")
        for idx, opt in enumerate(q['options']):
            label = chr(ord('A') + idx)
            print(f"   {label}. {opt}")
        correct = chr(ord('A') + q['answer_index'])
        print(f"   [Answer: {correct}]\n")


def main():
    parser = argparse.ArgumentParser(description="Simple MCQ generator")
    parser.add_argument("-f", "--file", help="Path to text file", default=None)
    parser.add_argument("-n", "--num", help="Number of questions", type=int, default=3)
    parser.add_argument("text", nargs="*", help="Input text (if no -f supplied)")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = " ".join(args.text).strip()
    if not text:
        print("No input text provided. Please pass a paragraph or -f <file>.")
        sys.exit(1)

    mcqs = generate_mcqs(text, num_qs=args.num)
    if not mcqs:
        print("Couldn't generate MCQs from the given text (try a longer paragraph).")
        sys.exit(0)
    print_mcqs(mcqs)


if __name__ == "__main__":
    main()
