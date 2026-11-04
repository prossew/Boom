using Xunit;
using AppRequests.Services;

namespace AppRequests.Tests
{
    public class PhoneValidatorTests
    {
        [Theory]
        [InlineData("+7 (912) 345-67-89", "79123456789")]
        [InlineData("89123456789", "79123456789")]
        [InlineData("8 912 345 67 89", "79123456789")]
        [InlineData("8(912)345-67-89", "79123456789")]
        [InlineData("+79123456789", "79123456789")]
        public void TryNormalize_ValidFormats_ReturnsNormalized(string input, string expected)
        {
            Assert.True(PhoneValidator.TryNormalize(input, out string normalized));
            Assert.Equal(expected, normalized);
        }

        [Theory]
        [InlineData(null)]
        [InlineData("")]
        [InlineData("   ")]
        [InlineData("1234567890")]      // 10 цифр
        [InlineData("123456789012")]    // 12 цифр
        [InlineData("abcdefghijk")]     // буквы
        [InlineData("99123456789")]     // начинается с 9
        [InlineData("19123456789")]     // начинается с 1
        [InlineData("+7 912 345 67 8")] // 10 цифр
        public void TryNormalize_Invalid_ReturnsFalse(string input)
        {
            Assert.False(PhoneValidator.TryNormalize(input, out string normalized));
            Assert.Null(normalized);
        }
    }
}
