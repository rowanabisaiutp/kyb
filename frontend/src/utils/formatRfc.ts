export function formatRfc(rfc: string): string {
  return rfc.toUpperCase().trim();
}

export function isValidRfcFormat(rfc: string): boolean {
  return /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/.test(rfc.toUpperCase().trim());
}
