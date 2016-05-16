# GoTags

GoTags is a Sublime Text plugin to append or remove tags for Golang struct.

Functionality includes:

- Append JSON tag with snake cased field name or remove JSON tag
- Append XML tag with snake cased field name or remove XML tag
- Append Xorm tag with xorm field type or remove Xorm tag

## Usage

Via the keyboard shortcut: `Super + G`, `Super + T` on OSX or `Ctrl + G`, `Ctrl + T` on other platforms. Then choice the action you want.

** Makesure line `type STRUCT_NAME struct{` in select region. **

For example:

```golang
type Example struct {
    FieldOne int       ``         // int field
    FieldTwo string    `orig tag` // string field
    FieldThree time.Time // time field
}
```

Then select `type Example struct {` line (or this is current line) and type the shortcut, select action `JSON: Append tags`:

```golang
type Example struct {
	FieldOne	int	`json:"field_one"`         // int field
	FieldTwo	string	`orig tag json:"field_two"` // string field
	FieldThree	time.Time	`json:"field_three"` // time field
}
```

After save with gofmt:

```golang
type Example struct {
	FieldOne   int       `json:"field_one"`          // int field
	FieldTwo   string    `orig tag json:"field_two"` // string field
	FieldThree time.Time `json:"field_three"`        // time field
}
```

## Idea from:

[gotag](https://github.com/suifengRock/gotag): golang auto generate struct tag.
