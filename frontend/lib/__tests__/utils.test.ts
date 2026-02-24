import { cn } from "../utils";

describe("cn", () => {
  test("basic class concatenation", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  test("conditional classes", () => {
    expect(cn("foo", false, undefined, null, "bar")).toBe("foo bar");
  });

  test("array input", () => {
    expect(cn(["foo", "bar"], "baz")).toBe("foo bar baz");
  });

  test("tailwind-merge conflict handling", () => {
    expect(cn("px-2 px-4", "px-3")).toBe("px-3");
  });
});
