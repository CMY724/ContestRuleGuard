"""
End-to-end tests for ContestRuleGuard using Playwright.
Run: python -m pytest e2e/ -q
Requires: pip install playwright && playwright install chromium
"""

import pytest


@pytest.mark.asyncio
@pytest.mark.skip(reason="requires running backend + frontend servers")
async def test_full_workflow_create_project_upload_document() -> None:
    """Full user workflow: create project -> upload document -> view blocks."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")

        # Create project
        await page.fill('input[name="name"]', "E2E Test Project")
        await page.fill('input[name="competition_name"]', "Test Competition")
        await page.fill('input[name="track"]', "AI")
        await page.click('button[type="submit"]')

        # Wait for project card to appear
        await page.wait_for_selector(".project-card")
        await page.click(".project-card")

        # Switch to documents tab
        await page.click('button:has-text("规则文档")')

        # Upload a document
        await page.wait_for_selector('input[type="file"]')
        await page.set_input_files(
            'input[type="file"]',
            "eval/cases/sample_rule_notice.txt",
        )
        await page.click('button:has-text("上传并解析")')

        # Wait for document to appear
        await page.wait_for_selector(".doc-card")
        assert await page.locator(".doc-card").count() >= 1

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="requires running backend + frontend servers")
async def test_rules_page_shows_extracted_rules() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")

        # Click existing project
        await page.wait_for_selector(".project-card")
        await page.click(".project-card")

        # Switch to rules tab
        await page.click('button:has-text("规则管理")')

        # Check that rules appear
        await page.wait_for_selector(".rule-card", timeout=10000)
        count = await page.locator(".rule-card").count()
        assert count >= 1

        await browser.close()
