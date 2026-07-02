export function buildFeedXml(projectName: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<feed>
  <object>
    <name>${projectName}</name>
    <address>г. Тест, ул. E2E, 1</address>
    <buildings>
      <building>
        <flats>
          <flat>
            <flat_id>e2e-flat-1</flat_id>
            <status>FREE</status>
            <room>2</room>
            <floor>7</floor>
            <area>54.20</area>
            <price>12000000</price>
            <price_base>12500000</price_base>
          </flat>
        </flats>
      </building>
    </buildings>
  </object>
</feed>
`;
}
