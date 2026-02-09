package mfa

import (
	"time"

	"areax/control-plane/pkg/totp"
)

// ValidateTOTP validates a TOTP code against a secret
func ValidateTOTP(code string, secret string) (bool, error) {
	return totp.ValidateCode(code, secret)
}

// GenerateTOTP generates a TOTP code for testing
func GenerateTOTP(secret string) (string, error) {
	return totp.GenerateCode(secret, time.Now())
}
