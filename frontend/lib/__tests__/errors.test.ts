import { describe, it, expect } from "bun:test";
import {
  parseError,
  isAbortError,
  getErrorMessage,
  parseApiError,
} from "../errors";

describe("parseError", () => {
  it("Error对象返回message", () => {
    const error = new Error("测试错误消息");
    expect(parseError(error)).toBe("测试错误消息");
  });

  it("带message属性的对象返回message", () => {
    const obj = { message: "对象消息" };
    expect(parseError(obj)).toBe("对象消息");
  });

  it("message为非字符串类型会被转为字符串", () => {
    const obj = { message: 12345 };
    expect(parseError(obj)).toBe("12345");
  });

  it("字符串直接返回", () => {
    expect(parseError("字符串错误")).toBe("字符串错误");
  });

  it("null返回'null'", () => {
    expect(parseError(null)).toBe("null");
  });

  it("undefined返回'undefined'", () => {
    expect(parseError(undefined)).toBe("undefined");
  });

  it("数字转为字符串", () => {
    expect(parseError(42)).toBe("42");
    expect(parseError(0)).toBe("0");
    expect(parseError(-123)).toBe("-123");
  });

  it("布尔值转为字符串", () => {
    expect(parseError(true)).toBe("true");
    expect(parseError(false)).toBe("false");
  });

  it("空对象返回'[object Object]'", () => {
    expect(parseError({})).toBe("[object Object]");
  });
});

describe("isAbortError", () => {
  it("DOMException AbortError返回true", () => {
    const abortError = new DOMException("Aborted", "AbortError");
    expect(isAbortError(abortError)).toBe(true);
  });

  it("其他类型的DOMException返回false", () => {
    const otherError = new DOMException("Other", "NotFoundError");
    expect(isAbortError(otherError)).toBe(false);
  });

  it("普通Error返回false", () => {
    const error = new Error("普通错误");
    expect(isAbortError(error)).toBe(false);
  });

  it("普通对象返回false", () => {
    expect(isAbortError({ name: "AbortError" })).toBe(false);
    expect(isAbortError({})).toBe(false);
  });

  it("null返回false", () => {
    expect(isAbortError(null)).toBe(false);
  });

  it("undefined返回false", () => {
    expect(isAbortError(undefined)).toBe(false);
  });

  it("字符串返回false", () => {
    expect(isAbortError("AbortError")).toBe(false);
  });
});

describe("getErrorMessage", () => {
  it("AbortError返回fallback", () => {
    const abortError = new DOMException("Aborted", "AbortError");
    expect(getErrorMessage(abortError, "用户取消操作")).toBe("用户取消操作");
  });

  it("普通Error返回message", () => {
    const error = new Error("普通错误");
    expect(getErrorMessage(error, "回退消息")).toBe("普通错误");
  });

  it("空message返回fallback", () => {
    const error = new Error("");
    expect(getErrorMessage(error, "回退消息")).toBe("回退消息");
  });

  it("字符串错误返回字符串", () => {
    expect(getErrorMessage("字符串错误", "回退消息")).toBe("字符串错误");
  });

  it("null返回'null'字符串（parseError(null)是truthy）", () => {
    expect(getErrorMessage(null, "回退消息")).toBe("null");
  });
});

describe("parseApiError", () => {
  it("FastAPI数组格式错误 (带msg和loc)", () => {
    const err = {
      response: {
        data: {
          detail: [
            {
              loc: ["body", "field_name"],
              msg: "字段不能为空",
              type: "value_error.missing",
            },
          ],
        },
      },
    };
    expect(parseApiError(err)).toBe("field_name: 字段不能为空");
  });

  it("FastAPI数组格式错误 (loc有多层)", () => {
    const err = {
      response: {
        data: {
          detail: [
            {
              loc: ["body", "nested", "deep", "field"],
              msg: "无效值",
              type: "value_error",
            },
          ],
        },
      },
    };
    expect(parseApiError(err)).toBe("field: 无效值");
  });

  it("FastAPI数组格式错误 (无msg/loc) 返回JSON", () => {
    const err = {
      response: {
        data: {
          detail: [{ type: "value_error", msg: "只有msg没有loc" }],
        },
      },
    };
    expect(parseApiError(err)).toBe(
      JSON.stringify([{ type: "value_error", msg: "只有msg没有loc" }])
    );
  });

  it("FastAPI数组格式错误 (空数组) fallback到parseError", () => {
    const err = {
      response: {
        data: {
          detail: [],
        },
      },
    };
    expect(parseApiError(err)).toBe("[object Object]");
  });

  it("FastAPI字符串detail", () => {
    const err = {
      response: {
        data: {
          detail: "认证失败",
        },
      },
    };
    expect(parseApiError(err)).toBe("认证失败");
  });

  it("无response属性时fallback到parseError", () => {
    const error = new Error("网络错误");
    expect(parseApiError(error)).toBe("网络错误");
  });

  it("response无data时fallback到parseError", () => {
    const err = {
      response: {},
    };
    expect(parseApiError(err)).toBe("[object Object]");
  });

  it("data无detail时fallback到parseError", () => {
    const err = {
      response: {
        data: {},
      },
    };
    expect(parseApiError(err)).toBe("[object Object]");
  });

  it("detail为其他类型时fallback到parseError", () => {
    const err = {
      response: {
        data: {
          detail: 12345,
        },
      },
    };
    expect(parseApiError(err)).toBe("[object Object]");
  });

  it("null错误fallback到parseError", () => {
    expect(parseApiError(null)).toBe("null");
  });

  it("undefined错误fallback到parseError", () => {
    expect(parseApiError(undefined)).toBe("undefined");
  });
});
