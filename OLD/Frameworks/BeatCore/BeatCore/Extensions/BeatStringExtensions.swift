//
//  BeatStringExtensions.swift
//  Beat
//
//  Created by Lauri-Matti Parppei on 26.12.2022.
//  Copyright © 2022 Lauri-Matti Parppei. All rights reserved.
//

import Foundation

public extension String {
	/// Returns a substring with given `NSRange`
	func substring(range:NSRange) -> String {
		if (range.length == 0) { return "" }
		
		let start = index(startIndex, offsetBy: range.location)
		let end = index(startIndex, offsetBy: NSMaxRange(range))
		let strRange = start..<end
		
		return String(self[strRange])
	}
	
	/// Replaces given range with a string and returns a new string.
	func stringByReplacing(range:NSRange, withString string:String) -> String {
		let range = Range(range, in: self)
		let result = self.replacingCharacters(in: range!, with: string)
		return result
	}
	
	/// Returns the substring that contains the characters after first occurrence of the provided token.
	/// - Parameter token: The token
	/// - Returns: The substring that contains the characters after first occurrence of the provided token.
	func removeLeading(startWith token: String) -> String {
		if let token = range(of: token) {
			var newString = self
			newString.removeSubrange(startIndex..<token.upperBound)
			return newString
		}
		return self
	}
	
	/// Returns the substring that contains the characters before first occurrence of the provided token.
	///
	/// - Parameter token: The token
	/// - Returns: The substring that contains the characters before first occurrence of the provided token.
	func removeTrailing(startWith token: String) -> String {
		
		if let token = range(of: token) {
			var newString = self
			newString.removeSubrange(token.lowerBound..<endIndex)
			return newString
		}
		return self
	}
	
	/// Replaces the occurrences of the strings provided.
	///
	/// - Parameter strings: Strings to remove.
	/// - Returns: Updated string with the strings removed.
	func replacingOccurrences(strings: [String]) -> String {
		var updatedString = self
		for string in strings {
			updatedString = updatedString.replacingOccurrences(of: string, with: "")
		}
		return updatedString
	}
}

public extension StringProtocol {
	subscript(offset: Int) -> Character { self[index(startIndex, offsetBy: offset)] }
	subscript(range: Range<Int>) -> SubSequence {
		let startIndex = index(self.startIndex, offsetBy: range.lowerBound)
		return self[startIndex..<index(startIndex, offsetBy: range.count)]
	}
	subscript(range: ClosedRange<Int>) -> SubSequence {
		let startIndex = index(self.startIndex, offsetBy: range.lowerBound)
		return self[startIndex..<index(startIndex, offsetBy: range.count)]
	}
	subscript(range: PartialRangeFrom<Int>) -> SubSequence { self[index(startIndex, offsetBy: range.lowerBound)...] }
	subscript(range: PartialRangeThrough<Int>) -> SubSequence { self[...index(startIndex, offsetBy: range.upperBound)] }
	subscript(range: PartialRangeUpTo<Int>) -> SubSequence { self[..<index(startIndex, offsetBy: range.upperBound)] }
}

public extension StringProtocol {
    func slice(from: String, to: String) -> String? {
        guard let rangeFrom = range(of: from)?.upperBound else { return nil }
        guard let rangeTo = self[rangeFrom...].range(of: to)?.lowerBound else { return nil }
        return String(self[rangeFrom..<rangeTo])
    }
}
