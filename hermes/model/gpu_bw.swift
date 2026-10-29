// GPU memory bandwidth through Metal compute, copy and triad on float4 buffers. Usage: ./gpu_bw MIB_PER_BUFFER REPS
import Metal
import Foundation
let mib = Int(CommandLine.arguments[1])!, reps = Int(CommandLine.arguments[2])!
let dev = MTLCreateSystemDefaultDevice()!, q = dev.makeCommandQueue()!
let src = """
#include <metal_stdlib>
using namespace metal;
kernel void copyk(device const float4* a [[buffer(0)]], device float4* b [[buffer(1)]], uint i [[thread_position_in_grid]]) { b[i]=a[i]; }
kernel void triad(device const float4* b [[buffer(0)]], device const float4* c [[buffer(1)]], device float4* a [[buffer(2)]], uint i [[thread_position_in_grid]]) { a[i]=b[i]+3.0*c[i]; }
"""
let lib = try! dev.makeLibrary(source: src, options: nil)
let bytes = mib * 1048576, n = bytes / 16
let b1 = dev.makeBuffer(length: bytes, options: .storageModeShared)!, b2 = dev.makeBuffer(length: bytes, options: .storageModeShared)!, b3 = dev.makeBuffer(length: bytes, options: .storageModeShared)!
memset(b1.contents(), 1, bytes); memset(b2.contents(), 2, bytes); memset(b3.contents(), 0, bytes)
func run(_ name: String, _ bufs: [MTLBuffer], _ moved: Double) -> String {
    let p = try! dev.makeComputePipelineState(function: lib.makeFunction(name: name)!); var t = [Double]()
    for _ in 0..<(reps + 2) {
        let cb = q.makeCommandBuffer()!, e = cb.makeComputeCommandEncoder()!; e.setComputePipelineState(p)
        for (i, b) in bufs.enumerated() { e.setBuffer(b, offset: 0, index: i) }
        e.dispatchThreads(MTLSize(width: n, height: 1, depth: 1), threadsPerThreadgroup: MTLSize(width: 256, height: 1, depth: 1)); e.endEncoding(); cb.commit(); cb.waitUntilCompleted()
        t.append(cb.gpuEndTime - cb.gpuStartTime)
    }
    let s = Array(t.dropFirst(2)).sorted()
    return "{\"kind\":\"gpu_\(name)\",\"mib_per_buffer\":\(mib),\"reps\":\(reps),\"best_gbs\":\(String(format: "%.1f", moved / s[0] / 1e9)),\"median_gbs\":\(String(format: "%.1f", moved / s[s.count / 2] / 1e9)),\"worst_gbs\":\(String(format: "%.1f", moved / s[s.count - 1] / 1e9))}"
}
print(run("copyk", [b1, b2], 2.0 * Double(bytes)))
print(run("triad", [b1, b2, b3], 3.0 * Double(bytes)))
