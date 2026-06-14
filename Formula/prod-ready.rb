# typed: false
# frozen_string_literal: true

# Homebrew formula for prod-ready
# Production-readiness assessment CLI for applications
class ProdReady < Formula
  desc "Dynamic production-readiness assessment framework"
  homepage "https://github.com/johnberey19/prod-ready"
  license "MIT"

  # Updated automatically by CI/CD via action-homebrew-bump-formula
  # Source: PyPI sdist (contains all docs)
  url "https://files.pythonhosted.org/packages/source/p/prod-ready/prod-ready-0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"

  depends_on "python@3.11"

  def install
    python3 = Formula["python@3.11"]
    venv = virtualenv_create(libexec, python3.opt_bin/"python3.11")
    venv.pip_install_and_link buildpath

    # Install documentation files
    doc.install "README.md"
    doc.install "GETTING_STARTING.md" if File.exist?("GETTING_STARTING.md")
    doc.install "CONTRIBUTING.md" if File.exist?("CONTRIBUTING.md")
    doc.install "CHANGELOG.md" if File.exist?("CHANGELOG.md")

    # Install man page if available
    man1.install "docs/man/prod-ready.1" if File.exist?("docs/man/prod-ready.1")

    # Install shell completions
    bash_completion.install "completions/prod-ready.bash" if File.exist?("completions/prod-ready.bash")
    zsh_completion.install "completions/_prod-ready" if File.exist?("completions/_prod-ready")
    fish_completion.install "completions/prod-ready.fish" if File.exist?("completions/prod-ready.fish")
  end

  def caveats
    <<~EOS
      Documentation is installed to:
        #{doc}/README.md
        #{doc}/GETTING_STARTED.md
        #{doc}/CONTRIBUTING.md
        #{doc}/CHANGELOG.md

      Quick start:
        prod-ready --help
        prod-ready list-types
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/prod-ready version")
    assert_match "prod-ready", shell_output("#{bin}/prod-ready --help")
  end
end
