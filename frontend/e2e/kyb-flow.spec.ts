import { expect, test } from "@playwright/test";

async function createDossier(page: any, suffix: string) {
  await page.goto("/dossiers/new");
  await page.waitForLoadState("networkidle");
  const rfc = `ETE${Date.now().toString().slice(-7)}${suffix}0`;
  await page.fill('input[id="rfc"]', rfc);
  await page.fill('input[id="razon_social"]', `Test ${suffix} SA de CV`);
  await page.fill('input[id="representante_nombre"]', "Juan Test");
  await page.fill('input[id="representante_cargo"]', "Director");
  await page.click("button:has-text('Crear Expediente')");
  await page.waitForURL(/\/dossiers\/.+/, { timeout: 10000 });
  return rfc;
}

test.describe("KYB Platform E2E", () => {

  test("01 - Dashboard loads", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=KYB Platform")).toBeVisible();
    await expect(page.locator("h1:has-text('Dashboard')")).toBeVisible();
    await expect(page.locator("text=Expedientes Recientes")).toBeVisible();
  });

  test("02 - Navigate to dossier list", async ({ page }) => {
    await page.goto("/");
    await page.click("a:has-text('Expedientes')");
    await expect(page.locator("h1:has-text('Expedientes KYB')")).toBeVisible();
  });

  test("03 - Navigate to create dossier", async ({ page }) => {
    await page.goto("/dossiers/new");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=Datos de la Persona Moral")).toBeVisible();
    await expect(page.locator("text=Representante Legal")).toBeVisible();
  });

  test("04 - Create dossier and redirect", async ({ page }) => {
    const rfc = await createDossier(page, "A");
    await expect(page.locator(`text=${rfc}`).first()).toBeVisible();
    await expect(page.locator("text=General").first()).toBeVisible();
  });

  test("05 - Dossier detail shows all tabs", async ({ page }) => {
    await createDossier(page, "B");
    for (const tab of ["General", "Documentos", "Listas Fiscales", "Conciliacion", "Riesgo", "Auditoria"]) {
      await expect(page.locator(`button:has-text('${tab}'), a:has-text('${tab}')`).first()).toBeVisible();
    }
  });

  test("06 - Document checklist shows 0/5", async ({ page }) => {
    await createDossier(page, "C");
    await expect(page.locator("text=0/5")).toBeVisible();
  });

  test("07 - Upload document", async ({ page }) => {
    await createDossier(page, "D");
    await page.click("button:has-text('Documentos')");
    await page.waitForTimeout(500);

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: "test_acta.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4 fake pdf for e2e"),
    });
    await page.click("button:has-text('Subir Documento')");
    await page.waitForTimeout(3000);
    await expect(page.locator("text=test_acta.pdf")).toBeVisible();
  });

  test("08 - Fiscal check", async ({ page }) => {
    await createDossier(page, "E");
    await page.click("button:has-text('Listas Fiscales')");
    await page.waitForTimeout(500);
    await page.click("button:has-text('Consultar Listas')");
    await page.waitForTimeout(5000);
    await expect(page.locator("text=Limpio").first()).toBeVisible();
  });

  test("09 - Risk score calculation", async ({ page }) => {
    await createDossier(page, "F");
    await page.click("button:has-text('Riesgo')");
    await page.waitForTimeout(500);
    await page.click("button:has-text('Calcular Score')");
    await page.waitForTimeout(3000);
    await expect(page.locator("text=puntos")).toBeVisible();
    await expect(page.locator("text=Acciones Sugeridas")).toBeVisible();
  });

  test("10 - Audit log", async ({ page }) => {
    await createDossier(page, "G");
    await page.click("button:has-text('Auditoria')");
    await page.waitForTimeout(1000);
    await expect(page.locator("text=Expediente creado")).toBeVisible();
  });

  test("11 - Status transition", async ({ page }) => {
    await createDossier(page, "H");
    await expect(page.locator("text=Borrador").first()).toBeVisible();
    await page.click("button:has-text('Iniciar Revision')");
    await page.waitForTimeout(2000);
    await expect(page.locator("text=En Revision").first()).toBeVisible();
  });

  test("12 - Not found page", async ({ page }) => {
    await page.goto("/pagina-que-no-existe");
    await expect(page.locator("text=Pagina no encontrada")).toBeVisible();
  });

  test("13 - Dashboard shows stats", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("text=Borradores")).toBeVisible();
  });
});
