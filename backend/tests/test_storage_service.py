from app.services.storage_service import generate_file_key, validate_file

import uuid


class TestValidateFile:
    def test_valid_pdf(self):
        assert validate_file("application/pdf", 1024) is None

    def test_valid_jpeg(self):
        assert validate_file("image/jpeg", 1024) is None

    def test_valid_png(self):
        assert validate_file("image/png", 1024) is None

    def test_invalid_type(self):
        result = validate_file("text/javascript", 1024)
        assert result is not None
        assert "no permitido" in result

    def test_too_large(self):
        result = validate_file("application/pdf", 11 * 1024 * 1024)
        assert result is not None
        assert "grande" in result

    def test_exact_limit(self):
        assert validate_file("application/pdf", 10 * 1024 * 1024) is None


class TestGenerateFileKey:
    def test_format(self):
        key = generate_file_key(uuid.uuid4(), "acta_constitutiva", "test.pdf")
        assert key.startswith("dossiers/")
        assert "/acta_constitutiva/" in key
        assert key.endswith(".pdf")

    def test_no_extension(self):
        key = generate_file_key(uuid.uuid4(), "otro", "document")
        assert key.endswith(".bin")

    def test_unique(self):
        did = uuid.uuid4()
        key1 = generate_file_key(did, "csf", "a.pdf")
        key2 = generate_file_key(did, "csf", "a.pdf")
        assert key1 != key2
