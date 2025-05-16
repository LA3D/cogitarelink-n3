def main():
    # Apply the CogitareLink sandbox patch for N3/EYE
    # Apply sandbox and tool patches for EYE reasoning
    try:
        import patch_reason_sandbox  # noqa: F401
        import patch_reason_tool     # noqa: F401
    except ImportError:
        pass
    print("Hello from n3-eye! CogitareLink EYE integration is patched.")


if __name__ == "__main__":
    main()
