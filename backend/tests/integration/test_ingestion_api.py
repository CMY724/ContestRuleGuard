from io import BytesIO

from docx import Document

DOCX_MT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_upload_document_returns_201_then_200_for_duplicate(client) -> None:
    response = client.post(
        "/api/projects",
        json={
            "name": "ingestion-int",
            "competition_name": "全国大学生算法大赛",
            "competition_year": 2026,
            "track": "AI",
            "target_stage": "national",
        },
    )
    assert response.status_code == 201, response.text
    project_id = response.json()["id"]

    docx = Document()
    docx.add_paragraph("第一条：参赛选手必须为在校全日制本科生。")
    buffer = BytesIO()
    docx.save(buffer)
    buffer.seek(0)

    upload = client.post(
        f"/api/projects/{project_id}/documents",
        data={"source_tier": "primary", "stage": "school"},
        files={"file": ("rule.docx", buffer, DOCX_MT)},
    )
    assert upload.status_code == 201, upload.text
    document = upload.json()
    assert document["filename"] == "rule.docx"
    assert document["source_tier"] == "primary"
    assert document["stage"] == "school"
    assert len(document["units"]) >= 1

    buffer.seek(0)
    duplicate = client.post(
        f"/api/projects/{project_id}/documents",
        data={"source_tier": "primary", "stage": "school"},
        files={"file": ("rule-dup.docx", buffer, DOCX_MT)},
    )
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["id"] == document["id"]
