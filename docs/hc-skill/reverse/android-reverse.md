---
comments: true
---

# Android程序逆向

> REVERSE · 知识域。APK/NDK 层逆向。标签:**DEX逆向**、**Native逆向**、**其他Android程序逆向**。

## 触发特征

- `.apk/.dex` 文件;Java/Kotlin 层 + native `.so` 混合。

## DEX逆向

- 工具:jadx(首选)/JEB/apktool;GDA 国产工具。
- 入口:AndroidManifest(exported 组件)→ Application/MainActivity。
- 校验逻辑:字符串比较、加密库调用(SecretKeySpec/ Cipher)定位 key。
- 对抗:混淆(ProGuard/R8/DexGuard)、字符串加密、DEX 壳(梆梆/爱加密/360:dump dex → FDex2/BlackDex/frida-dexdump)。
- 运行时 DEX patch:/proc/self/maps 定位内存 dex(Google CTF 2017);smali 注入绕组件(TAMUctf 2019);新工程引用原 .so 绕加载校验(Codegate CTF 2018)。
-JNI 注册混淆:RegisterNatives 动态注册 → frida hook 定位(HTB WonderSMS)。

## Native逆向

- `.so` 用 IDA/Ghidra 分析(ARM/AArch64);JNI 桥:`Java_包名_类名_方法名` 或动态注册。
- 关键:参数解包(jstring → GetStringUTFChars)、返回构造。
- Frida 动态:
  - hook native 函数打印参数/返回(`Interceptor.attach`)。
  - 证书锁定绕过(SSL pinning bypass,h1702ctf 2017)。
  - native key dump:内存搜索/函数返回值抓取(HackIT 2017)。
- 栈字符串、Ollvm 混淆 native 层(→ [静态分析对抗](anti-static.md))。

## 其他Android程序逆向

- **Flutter**:Dart AOT 快照 → Blutter 恢复类与方法;无 java 层。
- **鸿蒙 HarmonyOS**:HAP/ABC 字节码 → abc-decompiler。
- **Unity 游戏**:Il2CppDumper + GameAssembly.dll;Mono → dnSpy Assembly-CSharp.dll 运行时 patch(SECCON 2018)。
- **APK 签名校验**:签名 SHA-256 当 AES key(ASIS Finals 2018)——重新签名后逻辑变化。
- **反调试**:TracerPid/su/属性检测绕过(h1702ctf 2017);log 泄露 key(HackIT 2017)。
- **协议层**:HTTPS 抓包配合 Frida 绕 pinning;本地 SQLite/assets 加密库分析。
- **加固识别表**:梆梆/爱加密/娜迦/360/腾讯乐固特征(assets/lib 名)。

## 通用流程

1. apktool/jadx 静态走读 → 定关键函数。
2. 壳/混淆先处理(dump dex / 还原符号)。
3. native 不清楚 → Frida 动态桥接。
4. 校验绕过:patch smali 重打包 或 hook 返回值。
5. 重打包签名:`apksigner sign`(注意签名相关逻辑)。

## 工具速查

```bash
jadx-gui app.apk
frida -U -l hook.js com.target.app
blackdex / frida-dexdump       # 脱壳
objdump -d libnative.so        # 或 IDA arm64
```

## 转向

- smali/DEX 字节码细节 → [低级语言分析](low-level-lang.md);native 混淆 → [静态分析对抗](anti-static.md)
