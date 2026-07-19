from app.services.text_normalization_service import (
    canonical_search_form,
    fold_kannada_for_matching,
    normalize_terms,
    normalize_unicode,
    remove_zero_width_characters,
)


def assert_equal(
    actual: object,
    expected: object,
    description: str,
) -> None:
    if actual != expected:
        raise AssertionError(
            f"{description}\n"
            f"Expected: {expected!r}\n"
            f"Actual:   {actual!r}"
        )

    print(
        f"PASS: {description}"
    )


def main() -> None:
    assert_equal(
        normalize_unicode(
            "Dr RAJKUMAR"
        ),
        "dr rajkumar",
        "Unicode normalization case-folds English text",
    )

    assert_equal(
        remove_zero_width_characters(
            "ರಾಜ್\u200cಕುಮಾರ್"
        ),
        "ರಾಜ್‌ಕುಮಾರ್".replace(
            "\u200c",
            "",
        ),
        "Zero-width characters are removed",
    )

    assert_equal(
        fold_kannada_for_matching(
            "ರಾಜ್\u200cಕುಮಾರ್"
        ),
        fold_kannada_for_matching(
            "ರಾಜಕುಮಾರ್"
        ),
        "Kannada orthographic variants fold identically",
    )

    assert_equal(
        normalize_terms(
            "ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?"
        ),
        [
            "ರಾಜಕುಮಾರ್",
        ],
        "Generic Kannada query words are excluded",
    )

    assert_equal(
        canonical_search_form(
            "ಡಾ. ರಾಜ್\u200cಕುಮಾರ್"
        ),
        canonical_search_form(
            "ಡಾ ರಾಜಕುಮಾರ್"
        ),
        "Canonical search forms match across variants",
    )

    assert_equal(
        fold_kannada_for_matching(
            "ವಿಷ್ಣುವರ್ಧನ್"
        )
        == fold_kannada_for_matching(
            "ರಾಜಕುಮಾರ್"
        ),
        False,
        "Unrelated Kannada names remain different",
    )

    print(
        "\nAll text-normalization tests passed."
    )


if __name__ == "__main__":
    main()