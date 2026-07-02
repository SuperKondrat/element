import { describe, expect, it } from "vitest";
import { formatRooms } from "./format";

describe("formatRooms", () => {
  it("labels a zero-room lot as a studio", () => {
    expect(formatRooms(0)).toBe("Студия");
  });

  it.each([1, 2, 3, 4])("labels %i rooms as N-комн.", (rooms) => {
    expect(formatRooms(rooms)).toBe(`${rooms}-комн.`);
  });
});
