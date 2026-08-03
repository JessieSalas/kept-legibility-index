// visionocr · the machine reader for the Kept Readability Index.
// Reads images with Apple's Vision framework, language correction OFF,
// and prints "path<TAB>recognized text" per file. Settings are printed to
// stderr at startup so every run is self-documenting.
//
// Build:  swiftc -O -o visionocr visionocr.swift
import Foundation
import Vision
import AppKit

FileHandle.standardError.write(Data("""
visionocr settings:
  recognitionLevel = .accurate
  usesLanguageCorrection = false
  recognitionLanguages = [en-US] (pinned; the corpus is English)
  VNRecognizeTextRequest revision = \(VNRecognizeTextRequest().revision)
  macOS = \(ProcessInfo.processInfo.operatingSystemVersionString)

""".utf8))

for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("\(path)\t")
        continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([req])
    let text = (req.results ?? [])
        .compactMap { $0.topCandidates(1).first?.string }
        .joined(separator: " ")
    print("\(path)\t\(text)")
}
